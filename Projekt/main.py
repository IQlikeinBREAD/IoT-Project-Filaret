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
    reported_properties = {"Device" + str(machine.node)[-1]:}

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
