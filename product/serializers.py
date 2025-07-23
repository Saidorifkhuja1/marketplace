from rest_framework import serializers

from comment.serializers import CommentSerializer
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['uid', 'name']



class ProductCommentSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['uid', 'owner']



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['uid', 'owner']


