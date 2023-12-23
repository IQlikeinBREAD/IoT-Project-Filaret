import asyncio

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
        self.production_status = await self.client.get_node(f"{self.node}/ProductionStatus").get_value()
        self.work_order_id = await self.client.get_node(f"{self.node}/WorkorderId").get_value()
        self.production_rate = await self.client.get_node(f"{self.node}/ProductionRate").get_value()
        self.good_count = await self.client.get_node(f"{self.node}/GoodCount").get_value()
        self.bad_count = await self.client.get_node(f"{self.node}/BadCount").get_value()
        self.temperature = await self.client.get_node(f"{self.node}/Temperature").get_value()

    def data(self):
        return{
            "production_status": self.production_status,
            "work_order_id": self.work_order_id,
            "production_rate": self.production_rate,
            "good_count": self.good_count,
            "bad_count": self.bad_count,
            "temperature": self.temperature,
        }
    async def device_errors(self):
        self.device_error = await self.client.get_node(f"{self.node}/DeviceError").getvalue()
        binary_error = f'{self.device_error:04b}'
        binary_error_list = [int(bit) for bit in binary_error]
        while len(binary_error_list) < 4:  # Додавання нулів, якщо довжина списку менше 4
            binary_error_list.insert(0, 0)
        return binary_error_list
        
    
        
