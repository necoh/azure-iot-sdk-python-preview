# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from . import errors
from . import errors_paho
import paho.mqtt.client as mqtt

# mapping of Paho conack rc codes to Error object classes
paho_conack_rc_to_error = {
    mqtt.CONNACK_REFUSED_PROTOCOL_VERSION: errors_paho.PahoConnectionRefusedProtocolVersionError,
    mqtt.CONNACK_REFUSED_IDENTIFIER_REJECTED: errors_paho.PahoConnectionRefusedIdentifierRejectedError,
    mqtt.CONNACK_REFUSED_SERVER_UNAVAILABLE: errors_paho.PahoConnectionRefusedServerUnavailableError,
    mqtt.CONNACK_REFUSED_BAD_USERNAME_PASSWORD: errors_paho.PahoConnectionRefusedBadUsernamePasswordError,
    mqtt.CONNACK_REFUSED_NOT_AUTHORIZED: errors_paho.PahoConnectionRefusedNotAuthorizedError,
}

# mapping of Paho rc codes to Error object classes
paho_rc_to_error = {
    mqtt.MQTT_ERR_NOMEM: errors_paho.PahoNoMemoryError,
    mqtt.MQTT_ERR_PROTOCOL: errors_paho.PahoProtocolError,
    mqtt.MQTT_ERR_INVAL: errors_paho.PahoInvalidArgsError,
    mqtt.MQTT_ERR_NO_CONN: errors_paho.PahoNoConnectionError,
    mqtt.MQTT_ERR_CONN_REFUSED: errors_paho.PahoConnectionRefusedError,
    mqtt.MQTT_ERR_NOT_FOUND: errors_paho.PahoNotFoundError,
    mqtt.MQTT_ERR_CONN_LOST: errors_paho.PahoConnectionLostError,
    mqtt.MQTT_ERR_TLS: errors_paho.PahoTLSError,
    mqtt.MQTT_ERR_PAYLOAD_SIZE: errors_paho.PahoPayloadSizeError,
    mqtt.MQTT_ERR_NOT_SUPPORTED: errors_paho.PahoNotSupportedError,
    mqtt.MQTT_ERR_AUTH: errors_paho.PahoAuthError,
    mqtt.MQTT_ERR_ACL_DENIED: errors_paho.PahoACLDeniedError,
    mqtt.MQTT_ERR_UNKNOWN: errors_paho.PahoUnknownError,
    mqtt.MQTT_ERR_ERRNO: errors_paho.PahoUnknownError,
    mqtt.MQTT_ERR_QUEUE_SIZE: errors_paho.PahoQueueSizeError,
}

# mapping of Paho-specific errors to more generic errors
paho_error_to_generic_error = {
    errors_paho.PahoConnectionRefusedProtocolVersionError: errors.TransportError,
    errors_paho.PahoConnectionRefusedIdentifierRejectedError: errors.TransportError,
    errors_paho.PahoConnectionRefusedServerUnavailableError: errors.ConnectionFailedError,
    errors_paho.PahoConnectionRefusedBadUsernamePasswordError: errors.UnauthorizedError,
    errors_paho.PahoConnectionRefusedNotAuthorizedError: errors.UnauthorizedError,
    errors_paho.PahoNoMemoryError: errors.TransportError,
    errors_paho.PahoProtocolError: errors.TransportError,
    errors_paho.PahoInvalidArgsError: errors.TransportError,
    errors_paho.PahoNoConnectionError: errors.ConnectionDroppedError,
    errors_paho.PahoConnectionRefusedError: errors.UnauthorizedError,
    errors_paho.PahoNotFoundError: errors.TransportError,
    errors_paho.PahoConnectionLostError: errors.ConnectionDroppedError,
    errors_paho.PahoTLSError: errors.UnauthorizedError,
    errors_paho.PahoPayloadSizeError: errors.TransportError,
    errors_paho.PahoNotSupportedError: errors.TransportError,
    errors_paho.PahoAuthError: errors.UnauthorizedError,
    errors_paho.PahoACLDeniedError: errors.UnauthorizedError,
    errors_paho.PahoUnknownError: errors.TransportError,
    errors_paho.PahoQueueSizeError: errors.TransportError,
}


def _wrap_paho_error_in_generic_error(paho_error):
    """
    Return a generic error that wraps a paho-specific error

    :param Error paho_error: Instance of an Error returned from Paho operation
    :returns: Error that wraps that error
    """
    if paho_error.__class__ in paho_error_to_generic_error:
        generic_error = paho_error_to_generic_error[paho_error.__class__]
    else:
        generic_error = errors.TransportError

    # this makes an exception that shows the generic error as being caused by the paho error
    try:
        raise generic_error from paho_error
    except Exception as e:
        return e


def create_error_from_conack_rc_code(conack_rc_code):
    """
    Return an Error object from a failed Paho conack rc code

    :param int conack_rc_code: Code returned from failed operation
    :returns: Error object
    """
    message = mqtt.conack_string(conack_rc_code)
    if conack_rc_code in paho_conack_rc_to_error:
        paho_error = paho_conack_rc_to_error[conack_rc_code](message)
    else:
        paho_error = errors_paho.PahoUnknownError(message)

    return _wrap_paho_error_in_generic_error(paho_error)


def create_error_from_rc_code(rc):
    """
    Return an Error object from a failed Paho rc code

    :param int rc: Code returned from failed operation
    :returns: Error object
    """
    message = mqtt.error_string(rc)
    if rc in paho_rc_to_error:
        paho_error = paho_rc_to_error[rc](message)
    else:
        paho_error = errors_paho.PahoUnknownError(message)

    return _wrap_paho_error_in_generic_error(paho_error)
