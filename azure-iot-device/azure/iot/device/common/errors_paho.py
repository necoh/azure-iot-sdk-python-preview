# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class OperationCancelledError(Exception):
    """
    Operation was cancelled.
    """

    pass


class PahoConnectionRefusedProtocolVersionError(Exception):
    """
    Connection Refused: unacceptable protocol version.
    """

    pass


class PahoConnectionRefusedIdentifierRejectedError(Exception):
    """
    Connection Refused: identifier rejected.
    """

    pass


class PahoConnectionRefusedServerUnavailableError(Exception):
    """
    Connection Refused: broker unavailable.
    """

    pass


class PahoConnectionRefusedBadUsernamePasswordError(Exception):
    """
    Connection Refused: bad user name or password.
    """

    pass


class PahoConnectionRefusedNotAuthorizedError(Exception):
    """
    Connection Refused: not authorised.
    """

    pass


class PahoNoMemoryError(Exception):
    """
    Out of memory.
    """

    pass


class PahoProtocolError(Exception):
    """
    A network protocol error occurred when communicating with the broker.
    """

    pass


class PahoInvalidArgsError(Exception):
    """
    Invalid function arguments provided.
    """

    pass


class PahoNoConnectionError(Exception):
    """
    The client is not currently connected.
    """

    pass


class PahoConnectionRefusedError(Exception):
    """
    The connection was refused.
    """

    pass


class PahoNotFoundError(Exception):
    """
    Message not found (internal error).
    """

    pass


class PahoConnectionLostError(Exception):
    """
    The connection was lost.
    """

    pass


class PahoTLSError(Exception):
    """
    A TLS error occurred.
    """

    pass


class PahoPayloadSizeError(Exception):
    """
    Payload too large.
    """

    pass


class PahoNotSupportedError(Exception):
    """
    This feature is not supported.
    """

    pass


class PahoAuthError(Exception):
    """
    Authorisation failed.
    """

    pass


class PahoACLDeniedError(Exception):
    """
    Access denied by ACL.
    """

    pass


class PahoUnknownError(Exception):
    """
    Unknown error.
    """

    pass


class PahoQueueSizeError(Exception):
    """
    Outgoing queue is full or message already exists in queue
    """

    pass
