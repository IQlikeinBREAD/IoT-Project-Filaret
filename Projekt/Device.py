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
        self.emergency_stop = None

    async def wpisywanie(self):
        self.production_status = await self.client.get_node(f"{self.node}/ProductionStatus").get_value()
        self.work_order_id = await self.client.get_node(f"{self.node}/WorkorderId").get_value()
        self.production_rate = await self.client.get_node(f"{self.node}/ProductionRate").get_value()
        self.good_count = await self.client.get_node(f"{self.node}/GoodCount").get_value()
        self.bad_count = await self.client.get_node(f"{self.node}/BadCount").get_value()
        self.temperature = await self.client.get_node(f"{self.node}/Temperature").get_value()

    
        
