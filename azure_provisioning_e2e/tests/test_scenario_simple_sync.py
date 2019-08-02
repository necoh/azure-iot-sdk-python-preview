# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import time
from azure_provisioning_e2e.iothubservice20180630.service_helper import Helper
from azure.iot.device import ProvisioningDeviceClient
from azure.iot.device.common import X509
from provisioningserviceclient import (
    ProvisioningServiceClient,
    IndividualEnrollment,
    EnrollmentGroup,
)
from provisioningserviceclient.protocol.models import (
    AttestationMechanism,
    X509Attestation,
    ReprovisionPolicy,
)
from provisioningserviceclient.protocol.models import X509CertificateWithInfo, X509Certificates

# from provisioningserviceclient.models import AttestationMechanism , X509Attestation, ReprovisionPolicy
import pytest
import logging

# from scripts import create_x509_chain
import subprocess


logging.basicConfig(filename="example.log", level=logging.DEBUG)


dps_service_conn_str = "HostName=olkarDPS.azure-devices-provisioning.net;SharedAccessKeyName=provisioningserviceowner;SharedAccessKey=kC03gvTsxBEUCjizo6fZzVf37lwOKP7UHY6EVkoWMPg="
iothub_registry_read_conn_str = "HostName=IOTHubQuickStart.azure-devices.net;SharedAccessKeyName=registryRead;SharedAccessKey=btxB4/aGidQCdMHJJof6C6xsGkUwxQNtv58YfsaRipw="
provisioning_host = "global.azure-devices-provisioning.net"
id_scope = "0ne0004B56F"
leaf_certificate_path_1 = "../../scripts/demoCA/newcerts/device_cert1.pem"
leaf_certificate_key_1 = "../../scripts/demoCA/private/device_key1.pem"
leaf_certificate_password_1 = "hogwartsd"

leaf_certificate_path_2 = "../../scripts/demoCA/newcerts/device_cert2.pem"
leaf_certificate_key_2 = "../../scripts/demoCA/private/device_key2.pem"
leaf_certificate_password_2 = "hogwartsd"


@pytest.fixture(scope="module")
def before_module(request):
    print("set up before all tests")

    def after_module():
        print("tear down after all tests")

    request.addfinalizer(after_module)


@pytest.fixture(scope="function")
def before_test(request):
    print("set up before each test")

    def after_test():
        print("tear down after each test")

    request.addfinalizer(after_test)


@pytest.mark.it(
    "A device with a symmetric key individual enrollment is registered to IoTHub with the device id equal to the registration id"
)
def test_device_register_with_no_device_id_for_a_symmetric_key_individual_enrollment(
    before_module, before_test
):
    # dps_service_conn_str = "HostName=olkarDPS.azure-devices-provisioning.net;SharedAccessKeyName=provisioningserviceowner;SharedAccessKey=kC03gvTsxBEUCjizo6fZzVf37lwOKP7UHY6EVkoWMPg="
    # iothub_registry_read_conn_str = "HostName=IOTHubQuickStart.azure-devices.net;SharedAccessKeyName=registryRead;SharedAccessKey=btxB4/aGidQCdMHJJof6C6xsGkUwxQNtv58YfsaRipw="
    # provisioning_host = "global.azure-devices-provisioning.net"
    # id_scope = "0ne0004B56F"

    service_client = ProvisioningServiceClient.create_from_connection_string(dps_service_conn_str)

    registration_id = "e2e-dps-underthewhompingwillow"
    reprovision_policy = ReprovisionPolicy(migrate_device_data=True)
    attestation_mechanism = AttestationMechanism(type="symmetricKey")

    individual_provisioning_model = IndividualEnrollment.create(
        attestation=attestation_mechanism,
        registration_id=registration_id,
        reprovision_policy=reprovision_policy,
    )

    individual_enrollment_record = service_client.create_or_update(individual_provisioning_model)

    time.sleep(3)

    registration_id = individual_enrollment_record.registration_id
    symmetric_key = individual_enrollment_record.attestation.symmetric_key.primary_key

    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )

    provisioning_device_client.register()

    helper = Helper(iothub_registry_read_conn_str)
    device = helper.get_device(registration_id)

    assert device is not None
    assert device.authentication.type == "sas"
    assert device.device_id == registration_id


@pytest.mark.it(
    "A device with a symmetric key individual enrollment is registered to IoTHub with an user supplied custom device id"
)
def test_device_register_with_device_id_for_a_symmetric_key_individual_enrollment(before_test):
    # dps_service_conn_str = "HostName=olkarDPS.azure-devices-provisioning.net;SharedAccessKeyName=provisioningserviceowner;SharedAccessKey=kC03gvTsxBEUCjizo6fZzVf37lwOKP7UHY6EVkoWMPg="
    # iothub_registry_read_conn_str = "HostName=IOTHubQuickStart.azure-devices.net;SharedAccessKeyName=registryRead;SharedAccessKey=btxB4/aGidQCdMHJJof6C6xsGkUwxQNtv58YfsaRipw="
    # provisioning_host = "global.azure-devices-provisioning.net"
    # id_scope = "0ne0004B56F"

    registration_id = "e2e-dps-prioriincantatem"
    device_id = "e2e-dps-tommarvoloriddle"
    reprovision_policy = ReprovisionPolicy(migrate_device_data=True)
    attestation_mechanism = AttestationMechanism(type="symmetricKey")

    individual_provisioning_model = IndividualEnrollment.create(
        attestation=attestation_mechanism,
        registration_id=registration_id,
        device_id=device_id,
        reprovision_policy=reprovision_policy,
    )
    # provisioning_model = IndividualEnrollment(attestation=attestation_mechanism, registration_id=registration_id, device_id=device_id, reprovision_policy=reprovision_policy)

    service_client = ProvisioningServiceClient.create_from_connection_string(dps_service_conn_str)
    individual_enrollment_record = service_client.create_or_update(individual_provisioning_model)

    time.sleep(3)

    registration_id = individual_enrollment_record.registration_id
    symmetric_key = individual_enrollment_record.attestation.symmetric_key.primary_key

    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )

    provisioning_device_client.register()

    helper = Helper(iothub_registry_read_conn_str)
    device = helper.get_device(device_id)

    assert device is not None
    assert device.authentication.type == "sas"
    assert device.device_id == device_id


@pytest.mark.it(
    "A device with a X509 authentication individual enrollment is registered to IoTHub with an user supplied custom device id"
)
def test_device_register_with_device_id_for_a_x509_individual_enrollment(before_test):
    # subprocess.call("python create_x509_chain.py \"priori\" --ca-password \"hogwarts\" --intermediate-password \"hogwartsi\" --device-password \"hogwartsd\"", shell=True)

    registration_id = "devicepriori"  # the certificate common name
    device_id = "e2e-dps-flying-feather"
    reprovision_policy = ReprovisionPolicy(migrate_device_data=True)
    with open("../../scripts/demoCAOld/newcerts/device_cert.pem", "r") as device_pem:
        device_cert_content = device_pem.read()

    attestation_mechanism = AttestationMechanism.create_with_x509_client_certs(device_cert_content)

    individual_provisioning_model = IndividualEnrollment.create(
        attestation=attestation_mechanism,
        registration_id=registration_id,
        device_id=device_id,
        reprovision_policy=reprovision_policy,
    )

    # provisioning_model = IndividualEnrollment(attestation=attestation_mechanism,
    #                                           registration_id=registration_id, device_id=device_id,
    #                                           reprovision_policy=reprovision_policy)

    service_client = ProvisioningServiceClient.create_from_connection_string(dps_service_conn_str)
    individual_enrollment_record = service_client.create_or_update(individual_provisioning_model)

    time.sleep(3)

    registration_id = individual_enrollment_record.registration_id

    x509 = X509(
        cert_file=leaf_certificate_path_1,
        key_file=leaf_certificate_key_1,
        pass_phrase=leaf_certificate_password_1,
    )

    provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        x509=x509,
    )

    provisioning_device_client.register()

    helper = Helper(iothub_registry_read_conn_str)
    device = helper.get_device(device_id)

    assert device is not None
    assert device.authentication.type == "selfSigned"
    assert device.device_id == device_id


@pytest.mark.it(
    "A device with a X509 authentication individual enrollment is registered to IoTHub with the registration id"
)
def test_device_register_with_no_device_id_for_a_x509_individual_enrollment(before_test):
    # subprocess.call("python create_x509_chain.py \"priori\" --ca-password \"hogwarts\" --intermediate-password \"hogwartsi\" --device-password \"hogwartsd\"", shell=True)

    registration_id = "deviceincantatem"  # the certificate common name
    # device_id = "e2e-dps-flying-feather"
    reprovision_policy = ReprovisionPolicy(migrate_device_data=True)
    with open("../../scripts/demoCAOld2/newcerts/device_cert.pem", "r") as device_pem:
        device_cert_content = device_pem.read()

    attestation_mechanism = AttestationMechanism.create_with_x509_client_certs(device_cert_content)

    individual_provisioning_model = IndividualEnrollment.create(
        attestation=attestation_mechanism,
        registration_id=registration_id,
        reprovision_policy=reprovision_policy,
    )
    # provisioning_model = IndividualEnrollment(attestation=attestation_mechanism,
    #                                           registration_id=registration_id,
    #                                           reprovision_policy=reprovision_policy)

    service_client = ProvisioningServiceClient.create_from_connection_string(dps_service_conn_str)
    individual_enrollment_record = service_client.create_or_update(individual_provisioning_model)

    time.sleep(3)

    registration_id = individual_enrollment_record.registration_id

    x509 = X509(
        cert_file=leaf_certificate_path_1,
        key_file=leaf_certificate_key_1,
        pass_phrase=leaf_certificate_password_1,
    )

    provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        x509=x509,
    )

    provisioning_device_client.register()

    helper = Helper(iothub_registry_read_conn_str)
    device = helper.get_device(registration_id)

    assert device is not None
    assert device.authentication.type == "selfSigned"
    assert device.device_id == registration_id


@pytest.mark.it(
    "A device with a X509 authentication individual enrollment is registered to IoTHub with the registration id"
)
def test_group_of_devices_register_with_no_device_id_for_a_x509_individual_enrollment(before_test):
    # subprocess.call("python create_x509_chain.py \"priori\" --ca-password \"hogwarts\" --intermediate-password \"hogwartsi\" --device-password \"hogwartsd\"", shell=True)

    group_id = "e2e-hogwarts-school"
    common_device_id = "deviceincantatem"  # the certificate common name
    common_device_password = "hogwartsd"
    reprovision_policy = ReprovisionPolicy(migrate_device_data=True)

    device_count_in_group = 3

    intermediate_cert_filename = "../../scripts/demoCA/newcerts/intermediate_cert.pem"
    with open(intermediate_cert_filename, "r") as intermediate_pem:
        intermediate_cert_content = intermediate_pem.read()

    attestation_mechanism = AttestationMechanism.create_with_x509_signing_certs(
        intermediate_cert_content
    )
    enrollment_group_provisioning_model = EnrollmentGroup.create(
        group_id, attestation=attestation_mechanism, reprovision_policy=reprovision_policy
    )
    # provisioning_model = IndividualEnrollment(attestation=attestation_mechanism,
    #                                           registration_id=registration_id,
    #                                           reprovision_policy=reprovision_policy)

    service_client = ProvisioningServiceClient.create_from_connection_string(dps_service_conn_str)
    service_client.create_or_update(enrollment_group_provisioning_model)

    time.sleep(3)
    # registration_id = group_enrollment_record.registration_id
    helper = Helper(iothub_registry_read_conn_str)

    common_device_key_input_file = "../../scripts/demoCA/private/device_key"
    common_device_cert_input_file = "../../scripts/demoCA/newcerts/device_cert"
    common_device_cert_output_file = "../../scripts/demoCA/newcerts/out_device_cert"
    for index in range(0, device_count_in_group):
        device_id = common_device_id + str(index + 1)
        device_key_input_file = common_device_key_input_file + str(index + 1) + ".pem"
        device_cert_input_file = common_device_cert_input_file + str(index + 1) + ".pem"
        device_cert_output_file = common_device_cert_output_file + str(index + 1) + ".pem"
        filenames = [device_cert_input_file, intermediate_cert_filename]
        with open(device_cert_output_file, "w") as outfile:
            for fname in filenames:
                with open(fname) as infile:
                    outfile.write(infile.read())
        x509 = X509(
            cert_file=device_cert_output_file,
            key_file=device_key_input_file,
            pass_phrase=common_device_password,
        )

        provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
            provisioning_host=provisioning_host,
            registration_id=device_id,
            id_scope=id_scope,
            x509=x509,
        )

        provisioning_device_client.register()

        device = helper.get_device(device_id)

        assert device is not None
        assert device.authentication.type == "selfSigned"
        assert device.device_id == device_id

    # x5091 = X509(
    #     cert_file=leaf_certificate_path_1,
    #     key_file=leaf_certificate_key_1,
    #     pass_phrase=leaf_certificate_password_1
    # )
    #
    # provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
    #     provisioning_host=provisioning_host,
    #     registration_id=registration_id,
    #     id_scope=id_scope,
    #     x509=x5091,
    # )
    # provisioning_device_client.register()
    #
    # x5092 = X509(
    #     cert_file=leaf_certificate_path_2,
    #     key_file=leaf_certificate_key_2,
    #     pass_phrase=leaf_certificate_password_2
    # )
    #
    # provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
    #     provisioning_host=provisioning_host,
    #     registration_id=registration_id,
    #     id_scope=id_scope,
    #     x509=x5092,
    # )
    #
    # provisioning_device_client.register()
