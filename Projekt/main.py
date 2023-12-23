import asyncio
import json
from asyncua import Client
from azure.iot.device import IoTHubDeviceClient
from Device import Device

# Клас Device, який ви описали

async def main():
    client = Client("opc.tcp://localhost:4840/")
    await client.connect()

    CONNECTION_STRING = "HostName=IoT-uni-filaret6.azure-devices.net;DeviceId=Test-Device;SharedAccessKey=su85C/QkrwIfSsc+j1EX0KRGY/tD4VJcNAIoTAnvDlk="
    string_for_message = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

    device_list = await client.get_objects_node().get_children()
    device_list = device_list[1:]

    devices = []

    for device_node in device_list:
        d = Device(client, device_node)
        await d.wpisywanie()
        
        # Отримання даних з пристрою в форматі, який можна відправити в Azure IoT Hub
        device_info = {
            "production_status": d.production_status,
            "work_order_id": d.work_order_id,
            "production_rate": d.production_rate,
            "good_count": d.good_count,
            "bad_count": d.bad_count,
            "temperature": d.temperature
            # Додайте інші дані, які ви хочете відправити
        }

        # Перетворення словника в JSON-подібний об'єкт
        message_body = json.dumps(device_info)

        # Відправлення повідомлення
        string_for_message.send_message(message_body)

    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())
