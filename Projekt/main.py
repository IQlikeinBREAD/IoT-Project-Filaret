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

def twin_patch_handler(twin_patch,device_list):
    try:
        print("Twin patch received")
        print(twin_patch)
        # asyncio.run(compare_production_rates(twin_patch, lst_devices))
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
