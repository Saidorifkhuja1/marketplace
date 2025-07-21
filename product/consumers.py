
from channels.generic.websocket import AsyncJsonWebsocketConsumer

class AdminProductNotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated and user.is_staff:  # Only admin connects
            self.group_name = "admin_unverified_products"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("admin_unverified_products", self.channel_name)

    async def new_unverified_product(self, event):
        await self.send_json({
            "type": "new_unverified_product",
            "product_id": event["product_id"],
            "name": event["name"],
            "owner": event["owner"],
            "cost": event["cost"]
        })