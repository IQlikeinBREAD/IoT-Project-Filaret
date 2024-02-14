import asyncio
from asyncua import Client
from azure.iot.device import IoTHubDeviceClient, Message, IoTHubModuleClient, MethodResponse, MethodRequest
import json
from Device import Device 

def send_to_iot(device_client, device):
    data = device.data()
    message = json.dumps(data)
    device_client.send_message(message)

def rep_twin(device_client,device):
    reported_properties = {device.get_name_device():{"ProductRate": device.production_rate,
                                                    "Errors": device.device_error }}
    device_client.patch_twin_reported_properties(reported_properties)

async def prod_rate_com(twin_patch,device_list):
    for device in device_list:
        name_device = device.get_name_device()
        if name_device in twin_patch.keys() and twin_patch[name_device] is not None and twin_patch[name_device]["ProductionRate"] != device.production_rate:
            await device.set_prod_rate()


async def desired_twin_receive(client,device_list):

    def twin_patch_handler(twin_patch):
        try:
            print("Twin patch received")
            print(twin_patch)
            asyncio.run(prod_rate_com(twin_patch, device_list))
        except Exception as e:
            print(f"{str(e)}")
    
    try:
        client.on_twin_desired_properties_patch_received = twin_patch_handler
    except Exception as e:
        print(f"{str(e)}")


async def emergency_stop(opc_client, device_name):
   
    emergency_stop = opc_client.get_node(f"ns=2;s={device_name}/EmergencyStop")
    node = opc_client.get_node(f"ns=2;s={device_name}")
    await node.call_method(emergency_stop)
    print("Emergency stop called. Success")


async def reset_errors_status(opc_client, device_name):
    
    reset_err = opc_client.get_node(f"ns=2;s={device_name}/ResetErrorStatus")
    node = opc_client.get_node(f"ns=2;s={device_name}")
    await node.call_method(reset_err)
    print("Reset error status called. Success")

async def take_direct_method(client, opc_client):
   
    def handle_method(request):
        try:
            print(f"Direct Method called: {request.name}")
            print(f"Request: {request}")
            print(f"Payload: {request.payload}")

            if request.name == "emergency_stop":
                device_name = request.payload["DeviceName"]
                asyncio.run(emergency_stop(opc_client, device_name))

            elif request.name == "reset_err_status":
                device_name = request.payload["DeviceName"]
                asyncio.run(reset_errors_status(opc_client, device_name))

            response_payload = "Method executed successfully"
            response = MethodResponse.create_from_method_request(request, 200, payload=response_payload)
            print(f"Response: {response}")
            print(f"Payload: {response.payload}")
            client.send_method_response(response)
            return response
        except Exception as e:
            print(f"Exception caught in handle_method: {str(e)}")

    try:
        client.on_method_request_received = handle_method
    except:
        pass

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
        
        await desired_twin_receive(iot_client,devices)
         
        #Errors
        for device in devices:
            if device.get_errors() != [0,0,0,0]:
                 send_to_iot(iot_client, device)
            #await rep_twin(iot_client,device)

        await take_direct_method(iot_client, client)
    
    client.disconnect()
    iot_client.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
