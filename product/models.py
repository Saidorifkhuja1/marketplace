import uuid
from django.db import models

from user.models import User


class Category(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=500)


class Product(models.Model):
    STATUS_CHOICES = [
        ('pending', 'PENDING'),
        ('active', 'ACTIVE'),
        ('sold_out', 'SOLD OUT'),

    ]
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=500)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.PositiveIntegerField(default=1)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    location = models.CharField(max_length=255)
    photos = models.JSONField(default=list)
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=10)

    def __str__(self):
        return self.name
