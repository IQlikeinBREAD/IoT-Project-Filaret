import asyncio
from asyncua import Client
from azure.iot.device import IoTHubDeviceClient
import json
from Device import Device  # Переконайтеся, що клас Device належить модулю Device

async def send_to_iot(device_client, device):
    data = device.data()
    message = json.dumps(data)
    device_client.send_message(message)

async def main():
    client = Client("opc.tcp://localhost:4840/")
    await client.connect()

    CONNECTION_STRING = "HostName=IoT-uni-filaret6.azure-devices.net;DeviceId=Test-Device;SharedAccessKey=su85C/QkrwIfSsc+j1EX0KRGY/tD4VJcNAIoTAnvDlk="
    string_for_message = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    while True:
        device_list = await client.get_objects_node().get_children()
        device_list = device_list[1:]

        devices = []

        for device_node in device_list:
            d = Device(client, device_node)
            await d.wpisywanie_danych()
            devices.append(d)
        
        for device in devices:
            device_error =  device.device_errors()
            print(device.device_errors())
            if device_error != [0, 0, 0, 0]:
                await send_to_iot(string_for_message, device)

if __name__ == '__main__':
    asyncio.run(main())
