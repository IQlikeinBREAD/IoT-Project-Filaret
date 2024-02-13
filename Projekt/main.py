import asyncio
from asyncua import Client
from azure.iot.device import IoTHubDeviceClient
import json
from Device import Device 

async def send_to_iot(device_client, device):
    data = device.data()
    message = json.dumps(data)
    device_client.send_message(message)

async def rep_twin(device_client,device):
    reported_properties = {device.get_name_device():{"ProductRate": device.production_rate,
                                                    "Errors": device.device_error }}
    device_client.patch_twin_properties(reported_properties)

async def prod_rate_com(twin_patch,device_list):
    for device in device_list:
        name_device = device.get_name_device()
        if name_device in twin_patch.keys() and twin_patch[name_device] is not None and twin_patch[name_device]["ProductionRate"] != device.production_rate:
            await device.set_prod_rate()

def twin_patch_handler(twin_patch,device_list):
    try:
        print("Twin patch received")
        print(twin_patch)
        asyncio.run(prod_rate_com(twin_patch, device_list))
    except Exception as e:
        print(f"{str(e)}")


async def desired_twin_receive(client):

    try:
        client.on_twin_desired_properties_patch_received = twin_patch_handler
    except Exception as e:
        print(f"{str(e)}")


async def main():
    client = Client("opc.tcp://localhost:4840/")
    await client.connect()

    CONNECTION_STRING = "HostName=IoT-uni-filaret6.azure-devices.net;DeviceId=Test-Device;SharedAccessKey=su85C/QkrwIfSsc+j1EX0KRGY/tD4VJcNAIoTAnvDlk="
    iot_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    iot_client.connect()
    
    twin = iot_client.get_twin()['reported']
    del twin["$version"]
    for key, value in twin.items():
        twin[key] = None
    iot_client.patch_twin_reported_properties(twin)

    while True:
        #Pobieramy dane
        device_list = await client.get_objects_node().get_children()
        device_list = device_list[1:]

        devices = []

        for device_node in device_list:
            d = Device(client, device_node)
            await d.wpisywanie_danych()
            devices.append(d)
        
        #Errors
        for device in devices:
            if device.get_errors() != [0,0,0,0]:
                await send_to_iot(iot_client, device)
    
    await client.disconnect()
    iot_client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
