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

async def twin_desired(manager_client, device_id, reported):
    desired_twin = {}

    del reported["$metadata"]
    del reported["$version"]

    for key, value in reported.items():
        desired_twin[key] = {"ProductionRate": value["ProductionRate"]}

    twin = manager_client.get_twin(device_id)
    twin_patch = Twin(properties=TwinProperties(desired=desired_twin))
    twin = manager_client.update_twin(device_id, twin_patch, twin.etag)

async def clear_desired_twin(manager, device_id):
    twin = manager.get_twin(device_id)
    des = twin.properties.desired
    del des["$metadata"]
    del des["$version"]
    for key, value in des.items():
        des[key] = None

    twin_patch = Twin(properties=TwinProperties(desired=des))
    twin = manager.update_twin(device_id, twin_patch, twin.etag)

async def clear_blob_storage(connection_str):
    blob_container_names = ['device-err', 'temperature-info', 'kpi-production']

    blob_service = BlobServiceClient.from_connection_string(connection_str)

    for blob_container_name in blob_container_names:
        try:
            blob_service.delete_container(blob_container_name)
        except:
            pass

    print("Blobs are cleared")

async def run_device_method(manager, method_name, dev_name):
    cd = CloudToDeviceMethod(method_name=method_name, payload={"DeviceName": dev_name})
    manager.invoke_device_method("test_device", cd)


async def run_emergency_stop(manager, dev_name):
    await run_device_method(manager, "emergency_stop", dev_name)


async def run_res_err_status(manager, dev_name):
    await run_device_method(manager, "reset_err_status", dev_name)

async def read_blobs(manager, device_id, connection_str, date_err, date_kpi):
    blob_container_names = ['device-err', 'temperature-info', 'kpi-production']

    blob_service_client = BlobServiceClient.from_connection_string(connection_str)

    ret_date_err = date_err
    ret_date_kpi = date_kpi

    for blob_container_name in blob_container_names:
        try:
            container_client = blob_service_client.get_container_client(blob_container_name)

            lst_blob_json = []

            for blob in container_client.list_blobs():
                data = container_client.download_blob(blob).readall()
                data = data.decode("utf-8")
                lst_blob_json.append(data.split('\r\n'))

            lst_dic_blob = []

            for i in range(len(lst_blob_json)):
                for j in range(len(lst_blob_json[i])):
                    lst_dic_blob.append(json.loads(lst_blob_json[i][j]))

            print(f"{blob_container_name.upper()} JSON: " + str(lst_blob_json))
            print(f"{blob_container_name.upper()} DIC: " + str(lst_dic_blob))

            if blob_container_name == 'device-err':
                for i in range(len(lst_dic_blob)):
                    if lst_dic_blob[i]["windowEndTime"] > date_err:
                        ret_date_err = lst_dic_blob[i]["windowEndTime"]
                        device_name = lst_dic_blob[i]["DeviceName"]
                        await run_emergency_stop(manager, device_name)

            elif blob_container_name == 'kpi-production':
                for i in range(len(lst_dic_blob)):
                    if lst_dic_blob[i]["windEndTime"] > date_kpi:
                        ret_date_kpi = lst_dic_blob[i]["windEndTime"]

                        if lst_dic_blob[i]["KPI"] < 90:
                            print("---------kpi------------")
                            twin = manager.get_twin(device_id)
                            des = twin.properties.desired

                            dev_name = "Device" + str(lst_dic_blob[i]["DeviceName"])[-1]
                            prod_rate = des[dev_name]["ProductionRate"] - 10

                            update_tw = {dev_name: {"ProductionRate": prod_rate}}

                            twin_patch = Twin(properties=TwinProperties(desired=update_tw))
                            twin = manager.update_twin(device_id, twin_patch, twin.etag)
        except:
            pass

    return ret_date_err, ret_date_kpi
