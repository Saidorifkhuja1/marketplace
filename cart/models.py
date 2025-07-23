import uuid

from django.db import models

from core import settings
from product.models import Product


class Cart(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.product.name} in {self.user.name}'s cart"


