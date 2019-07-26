# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.iot.device import ProvisioningDeviceClient
from provisioningserviceclient import ProvisioningServiceClient, IndividualEnrollment
from provisioningserviceclient.protocol.models import AttestationMechanism


def test_individual_enrollment_device_register():
    attestation_mechanism = AttestationMechanism(type="symmetricKey")
    conn_str = "HostName=olkarDPS.azure-devices-provisioning.net;SharedAccessKeyName=provisioningserviceowner;SharedAccessKey=kC03gvTsxBEUCjizo6fZzVf37lwOKP7UHY6EVkoWMPg="
    service_client = ProvisioningServiceClient.create_from_connection_string(conn_str)

    provisioning_model = IndividualEnrollment(attestation=attestation_mechanism, registration_id="underthewhompingwillow")
    individual_enrollment_record = service_client.create_or_update(provisioning_model)
    registration_id = individual_enrollment_record.registration_id
    symmetric_key = individual_enrollment_record.attestation.symmetric_key

    provisioning_host = "global.azure-devices-provisioning.net"
    id_scope = "0ne0004B56F"
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )

    provisioning_device_client.register()

    # assert from iothub service that it got registered