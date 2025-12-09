from rest_framework import serializers
from .models import Comment




class CommentSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.name', read_only=True)

    class Meta:
        model = Comment
        fields = ['uid', 'owner_name', 'body']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['product', 'body']