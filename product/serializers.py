# serializers.py
from rest_framework import serializers
from django.core.exceptions import ValidationError

from comment.serializers import CommentSerializer
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['uid', 'name']


class ProductSerializer(serializers.ModelSerializer):
    photos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'uid', 'name', 'cost', 'amount', 'owner', 'category',
            'description', 'location', 'status', 'created_at', 'updated_at',
            'photo1', 'photo2', 'photo3', 'photo4', 'photo5', 'photos'
        ]
        read_only_fields = ['uid', 'owner', 'created_at', 'updated_at']

    def get_photos(self, obj):
        """Return list of photo URLs"""
        request = self.context.get('request')
        photos = []

        for i in range(1, 6):
            photo = getattr(obj, f'photo{i}')
            if photo and request:
                photos.append(request.build_absolute_uri(photo.url))
            elif photo:
                photos.append(photo.url)

        return photos

    def validate(self, data):
        """Validate that at least photo1 is provided"""
        # For creation, photo1 is required
        if self.instance is None:  # Creating new instance
            if not data.get('photo1'):
                raise serializers.ValidationError({
                    'photo1': 'At least one photo is required.'
                })

        # For updates, if photo1 is being cleared, ensure it's not empty
        elif self.instance and 'photo1' in data:
            if not data.get('photo1') and not self.instance.photo1:
                raise serializers.ValidationError({
                    'photo1': 'At least one photo is required.'
                })

        return data


class ProductCommentSerializer(serializers.ModelSerializer):
    """Serializer for product detail view with comments"""
    comments = CommentSerializer(many=True, read_only=True)
    photos = serializers.SerializerMethodField(read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'uid', 'name', 'cost', 'amount', 'owner', 'owner_name',
            'category', 'category_name', 'description', 'location',
            'status', 'created_at', 'updated_at', 'photo1', 'photo2',
            'photo3', 'photo4', 'photo5', 'photos', 'comments'
        ]

    def get_photos(self, obj):
        """Return list of photo URLs"""
        request = self.context.get('request')
        photos = []

        for i in range(1, 6):
            photo = getattr(obj, f'photo{i}')
            if photo and request:
                photos.append(request.build_absolute_uri(photo.url))
            elif photo:
                photos.append(photo.url)

        return photos


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer specifically for create/update operations"""

    class Meta:
        model = Product
        fields = [
            'name', 'cost', 'amount', 'category', 'description',
            'location', 'status', 'photo1', 'photo2', 'photo3',
            'photo4', 'photo5'
        ]

    def validate(self, data):
        """Validate that at least photo1 is provided"""
        if not data.get('photo1'):
            raise serializers.ValidationError({
                'photo1': 'At least one photo is required.'
            })
        return data

    def to_representation(self, instance):
        """Use ProductSerializer for response"""
        serializer = ProductSerializer(instance, context=self.context)
        return serializer.data