# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import asyncio
from azure.iot.device.aio import ProvisioningDeviceClient

import logging

logging.basicConfig(level=logging.ERROR)

provisioning_host = os.getenv("PROVISIONING_HOST")
id_scope = os.getenv("PROVISIONING_IDSCOPE")
registration_id = os.getenv("PROVISIONING_REGISTRATION_ID")
symmetric_key = os.getenv("PROVISIONING_SYMMETRIC_KEY")


async def main():
    async def register_device():
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host=provisioning_host,
            registration_id=registration_id,
            id_scope=id_scope,
            symmetric_key=symmetric_key,
        )

        registration_result = await provisioning_device_client.register()
        return registration_result

    results = await asyncio.gather(register_device())
    registration_result = results[0]
    # print("The complete registration result is")
    # print(registration_result.registration_state)
    print("The device_id is:-")
    print(registration_result.registration_state.device_id)
    print("The assigned_hub is:-")
    print(registration_result.registration_state.assigned_hub)
    print("The status is:-")
    print(registration_result.status)


if __name__ == "__main__":
    asyncio.run(main())

    # If using Python 3.6 or below, use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
