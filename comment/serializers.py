from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.name', read_only=True)
    owner_id = serializers.CharField(source='owner.uid', read_only=True)

    class Meta:
        model = Comment
        fields = ['uid', 'owner_id', 'owner_name', 'body', 'created_at', 'updated_at']
        read_only_fields = ['uid', 'created_at', 'updated_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['product', 'body']


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['body']