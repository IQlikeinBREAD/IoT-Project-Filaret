import asyncio
from asyncua import Client,ua

class Device:
    def __init__(self,client,node):
        self.client = client
        self.node = node
        self.production_status = None
        self.work_order_id = None
        self.production_rate = None
        self.good_count = None
        self.bad_count = None
        self.temperature = None
        self.device_error = None

    async def wpisywanie_danych(self):
        {str(self.node)[7:]}
        self.production_status = await self.client.get_node(f"{self.node}/ProductionStatus").get_value()
        self.work_order_id = await self.client.get_node(f"{self.node}/WorkorderId").get_value()
        self.production_rate = await self.client.get_node(f"{self.node}/ProductionRate").get_value()
        self.good_count = await self.client.get_node(f"{self.node}/GoodCount").get_value()
        self.bad_count = await self.client.get_node(f"{self.node}/BadCount").get_value()
        self.temperature = await self.client.get_node(f"{self.node}/Temperature").get_value()
        self.device_error= await self.client.get_node(f"{self.node}/DeviceError").get_value()
        self.device_error = [int(num)for num in bin(self.device_error)[2:].zfill(4)]

    def data(self):
        return{
            "production_status": self.production_status,
            "work_order_id": self.work_order_id,
            "production_rate": self.production_rate,
            "good_count": self.good_count,
            "bad_count": self.bad_count,
            "temperature": self.temperature,
            "device_errors":self.device_error
        }
    
    async def get_errors(self):
        return self.device_error
    
    async def get_name_device(self):
        return str(self.node)[7:]
    
    async def set_prod_rate(self, value=10):
        await self.client.set_values([self.client.get_node(f"{self.node}/ProductionRate")],
                                [ua.DataValue(ua.Variant(int(self.production_rate - value), ua.VariantType.Int32))])
    
    async def emergency_stop(self):
        emer_Stop = self.client.get_node(f"{self.node}/EmergencyStop")
        await self.node.call_method(emer_Stop)

    async def reset_errors(self):
        reset = self.client.get_node(f"{self.node}/ResetErrorStatus")
        await self.node.call_method(reset)
