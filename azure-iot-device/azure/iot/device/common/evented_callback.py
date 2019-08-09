# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import threading
import logging

logger = logging.getLogger(__name__)


class EventedCallback(object):
    """
    A sync callback whose completion can be waited upon.
    """

    def __init__(self, return_arg_name=None):
        """
        Creates an instance of an EventedCallback.

        """
        self.completion_event = threading.Event()
        self.exception = None
        self.result = None

        def wrapping_callback(*args, **kwargs):
            if "error" in kwargs:
                self.exception = kwargs["error"]
            elif return_arg_name:
                if return_arg_name in kwargs:
                    self.results = kwargs[return_arg_name]
                else:
                    self.exception = TypeError(
                        "internal error: excepected named argument {}, did not get".format(
                            return_arg_name
                        )
                    )

            self.completion_event.set()

        self.callback = wrapping_callback

    def __call__(self, *args, **kwargs):
        """
        Calls the callback.
        """
        self.callback(*args, **kwargs)

    def wait(self, *args, **kwargs):
        """
        Wait for the callback to be called, and return the results.
        """
        self.completion_event.wait(*args, **kwargs)

        if self.exception:
            raise self.exception
        else:
            return self.result
