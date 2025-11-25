import uuid
from django.db import models

from product.models import Product
from user.models import User


class Comment(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()

    def __str__(self):
        return f"{self.owner} - {self.body[:30]}"