# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import logging

logger = logging.getLogger(__name__)


def exception_caught_in_background_thread(e):
    logger.error(msg="Exception caught in background thread.  Unable to handle.", exc_info=e)
