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
        request = self.context.get('request')
        photos = []

        for i in range(1, 6):
            photo = getattr(obj, f'photo{i}')
            if photo:
                photos.append(request.build_absolute_uri(photo.url) if request else photo.url)

        return photos

    def validate(self, data):
        if self.instance is None:  # create
            if not data.get('photo1'):
                raise serializers.ValidationError({
                    'photo1': 'At least one photo is required.'
                })
        return data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'cost', 'amount', 'category', 'description',
            'location', 'status', 'photo1', 'photo2', 'photo3',
            'photo4', 'photo5'
        ]

    def validate(self, data):
        # create
        if not self.instance and not data.get('photo1'):
            raise serializers.ValidationError({
                'photo1': 'At least one photo is required.'
            })

        # update
        if self.instance and not self.instance.photo1 and not data.get('photo1'):
            raise serializers.ValidationError({
                'photo1': 'At least one photo is required.'
            })

        # seller cannot activate product
        if self.context['request'].method in ['PUT', 'PATCH']:
            if data.get('status') == 'active':
                raise serializers.ValidationError({
                    'status': "You cannot set status to 'active'."
                })

        return data

    def to_representation(self, instance):
        return ProductSerializer(instance, context=self.context).data




class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'uid', 'name', 'cost', 'amount', 'category', 'description',
            'location', 'status', 'created_at', 'updated_at'
        ]
