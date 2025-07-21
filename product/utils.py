from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def notify_admin_unverified_product(product):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "admin_unverified_products",
        {
            "type": "new_unverified_product",
            "product_id": str(product.uid),
            "name": product.name,
            "owner": product.owner.email,
            "cost": float(product.cost)
        }
    )