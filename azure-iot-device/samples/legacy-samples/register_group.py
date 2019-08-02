# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


# This is for illustration purposes only. The sample will not work currently.

import os
import logging

from azure.iot.device.common import X509
from azure.iot.device import ProvisioningDeviceClient


logging.basicConfig(level=logging.DEBUG)

provisioning_host = os.getenv("PROVISIONING_HOST")
id_scope = os.getenv("PROVISIONING_IDSCOPE")

common_device_id = "deviceincantatem"  # the certificate common name
group_id = "e2e-hogwarts-school"
intermediate_cert_filename = "../../../scripts/demoCA/newcerts/intermediate_cert.pem"
common_device_key_input_file = "../../../scripts/demoCA/private/device_key"
common_device_cert_input_file = "../../../scripts/demoCA/newcerts/device_cert"
common_device_cert_output_file = "../../../scripts/demoCA/newcerts/out_device_cert"
for index in range(0, 3):
    device_id = common_device_id + str(index + 1)
    device_key_input_file = common_device_key_input_file + str(index + 1) + ".pem"
    device_cert_input_file = common_device_cert_input_file + str(index + 1) + ".pem"
    device_cert_output_file = common_device_cert_output_file + str(index + 1) + ".pem"
    filenames = [device_cert_input_file, intermediate_cert_filename]
    with open(device_cert_output_file, "w") as outfile:
        for fname in filenames:
            with open(fname) as infile:
                outfile.write(infile.read())

    # for index in range(0, 3):
    #     device_id = common_device_id + str(index + 1)
    #     device_cert_output_file = common_device_cert_output_file + str(index + 1) + ".pem"
    #     device_key_input_file = common_device_key_input_file + str(index + 1) + ".pem"
    x509 = X509(
        cert_file=device_cert_output_file, key_file=device_key_input_file, pass_phrase="hogwartsd"
    )
    provisioning_device_client = ProvisioningDeviceClient.create_from_x509_certificate(
        provisioning_host=provisioning_host, registration_id=device_id, id_scope=id_scope, x509=x509
    )
    provisioning_device_client.register()
