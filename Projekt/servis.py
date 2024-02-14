import asyncio
from azure.iot.hub import IoTHubRegistryManager
from azure.iot.hub.models import Twin, TwinProperties, CloudToDeviceMethod
from azure.storage.blob import BlobServiceClient
import json


async def receive_twin_reported(manager_client, device_id):
    twin = manager_client.get_twin(device_id)
    rep = twin.properties.reported
    print("Twin reported:")
    print(rep)
    return rep
