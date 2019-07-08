# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
import logging
import threading
from multiprocessing.pool import ThreadPool
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

"""
This module contains decorators that are used to marshal code into pipeline and
callback threads and to assert that code is being called in the correct thread.

The intention of these decorators is to ensure the following:

1. All pipeline functions execute in a single thread, known as the "pipeline
  thread".  The `invoke_on_pipeline_thread` and `invoke_on_pipeline_thread_nowait`
  decorators cause the decorated function to run on the pipeline thread.

2. If the pipeline thread is busy running a different function, the invoke
  decorators will wait until that function is complete before invoking another
  function on that thread.

3. There is a different thread which is used for callsbacks into user code, known
  as the the "callback thread".  This is not meant for callbacks into pipeline
  code.  Those callbacks should still execute on the pipeline thread.  The
  `invoke_on_callback_thread_nowait` decorator is used to ensure that callbacks
  execute on the callback thread.

4. Decorators which cause thread switches are used only when necessary.  The
  pipeline thread is only entered in places where we know that external code is
  calling into the pipeline (such as a client API call or a callback from a
  third-party library).  Likewise, the callback thread is only entered in places
  where we know that the pipeline is calling back into client code.

5. Exceptions raised from the pipeline thread are still able to be caught by
  the function which entered the pipeline thread.

5. Calls into the pipeline thread can either block or not block.  Blocking is used
  for cases where the caller needs a return value from the pipeline or is
  expecting to handle any errors raised from the pipeline thread.  Blocking is
  not used when the code calling into the pipeline is not waiting for a response
  and is not expecting to handle any exceptions, such as protocol library
  handlers which call into the pipeline to deliver protocol messages.

6. Calls into the callback thread could theretically block, but we currently
  only have decorators which enter the callback thread without blocking.  This
  is done to ensure that client code does not execute on the pipeline thread and
  also to ensure that the pipline thread is not blocked while waiting for client
  code to execute.

These decorators use concurrent.futures.Future and the ThreadPoolExecutor because:

1. The thread pooling with a pool size of 1 gives us a single thread to run all
  pipeline operations and a different (single) thread to run all callbacks.  If
  the code attempts to run a second pipeline operation (or callback) while a
  different one is running, the ThreadPoolExecutor will queue the code until the
  first call is completed.

2. The concurent.futures.Future object properly handles both Exception and
  BaseException errors, re-raising them when the Future.result method is called.
  threading.Thread.get() was not an option because it doesn't re-raise
  BaseException errors when Thread.get is called.

3. concurrent.futures is available as a backport to 2.7.

"""


def _get_named_executor(thread_name):
    """
    Get a ThreadPoolExecutor object with the given name.  If no such executor exists,
    this function will create on with a single worker and assign it to the provided
    name.
    """
    executor = getattr(_get_named_executor, thread_name, None)
    if not executor:
        logger.info("Creating {} executor".format(thread_name))
        executor = ThreadPoolExecutor(max_workers=1)
        setattr(_get_named_executor, thread_name, ThreadPoolExecutor(max_workers=1))
    return executor


def _get_thread_local_storage():
    """
    Get an object which contains "thread local storage" using the threading.local()
    function.  If no such object exists, one is created.  The object returned from
    `threading.local()` appears to be a global object, but has a different value for
    each individual thread.  We use this so we can check which thread we're running
    inside at runtime.
    """
    if not getattr(_get_thread_local_storage, "local", None):
        logger.info("Creating thread local storage")
        _get_thread_local_storage.local = threading.local()
    return _get_thread_local_storage.local


def _invoke_on_executor_thread(thread_name, block=True, _func=None):
    """
    Decorator which runs the wrapped function on a given thread.  If block==False,
    the call returns immediately without waiting for the decorated function to complete.
    If block==True, the call waits for the decorated function to complete before returning.
    """

    def decorator(func):
        function_name = getattr(func, "__name__", str(func))

        def wrapper(*args, **kwargs):
            if not getattr(_get_thread_local_storage(), "in_{}_thread".format(thread_name), False):
                logger.info("Starting {} in {} thread".format(function_name, thread_name))

                def thread_proc():
                    setattr(_get_thread_local_storage(), "in_{}_thread".format(thread_name), True)
                    return func(*args, **kwargs)

                # TODO: add a timeout here and throw exception on failure
                future = _get_named_executor(thread_name).submit(thread_proc)
                if block:
                    return future.result()
                else:
                    return future
            else:
                logger.debug("Already in {} thread for {}".format(thread_name, function_name))
                return func(*args, **kwargs)

        # Silly hack:  On 2.7, we can't use @functools.wraps on callables don't have a __name__ attribute
        # attribute(like MagicMock object), so we only do it when we have a name.  functools.update_wrapper
        # below is the same as using the @functools.wraps(func) decorator on the wrapper function above.
        if getattr(func, "__name__", None):
            return functools.update_wrapper(wrapped=func, wrapper=wrapper)
        else:
            return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def invoke_on_pipeline_thread(_func=None):
    """
    Run the decorated function on the pipeline thread.
    """
    return _invoke_on_executor_thread(thread_name="pipeline", _func=_func)


def invoke_on_pipeline_thread_nowait(_func=None):
    """
    Run the decorated function on the pipeline thread, but don't wait for it to complete
    """
    return _invoke_on_executor_thread(thread_name="pipeline", block=False, _func=_func)


def invoke_on_callback_thread_nowait(_func=None):
    """
    Run the decorated function on the callback thread, but don't wait for it to complete
    """
    return _invoke_on_executor_thread(thread_name="callback", block=False, _func=_func)


def _assert_executor_thread(thread_name, _func=None):
    """
    Decorator which asserts that the given function only gets called inside the given
    thread.
    """

    def decorator(func):
        function_name = getattr(func, "__name__", str(func))

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not getattr(_get_thread_local_storage(), "in_{}_thread".format(thread_name), False):
                assert False, """Function {function_name} is not running inside {thread_name} thread.
                    It should be. You should use invoke_on_{function_name}_thread(_nowait) to enter the
                    {thread_name} thread before calling this function.  If you're hitting this from
                    inside a test function, you may need to add the fake_pipeline_thread fixture to
                    your test.  (grep for apply_fake_pipeline_thread).""".format(
                    function_name=function_name, thread_name=thread_name
                )

            return func(*args, **kwargs)

        return wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)


def runs_on_pipeline_thread(_func=None):
    """
    Decorator which marks a function as only running inside the pipeline thread.
    """
    return _assert_executor_thread(thread_name="pipeline", _func=_func)
