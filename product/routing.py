from django.urls import re_path
from .consumers import AdminProductNotificationConsumer

websocket_urlpatterns = [
    re_path(r"ws/admin/products/unverified/$", AdminProductNotificationConsumer.as_asgi()),
]