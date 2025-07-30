
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from user.models import User


class Category(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=500)

    def __str__(self):
        return self.name


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
    status = models.CharField(choices=STATUS_CHOICES, default='pending', max_length=10)


    photo1 = models.ImageField(upload_to='products/', blank=True, null=True)
    photo2 = models.ImageField(upload_to='products/', blank=True, null=True)
    photo3 = models.ImageField(upload_to='products/', blank=True, null=True)
    photo4 = models.ImageField(upload_to='products/', blank=True, null=True)
    photo5 = models.ImageField(upload_to='products/', blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_photos(self):
        """Return list of all non-empty photos"""
        photos = []
        for i in range(1, 6):
            photo = getattr(self, f'photo{i}')
            if photo:
                photos.append(photo)
        return photos

    def get_photos_urls(self):
        """Return list of photo URLs"""
        urls = []
        for i in range(1, 6):
            photo = getattr(self, f'photo{i}')
            if photo:
                urls.append(photo.url)
        return urls


    # def clean(self):
    #     # Ensure at least one photo is provided
    #     if not self.photo1:
    #         raise ValidationError("At least one photo is required.")


