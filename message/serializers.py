from rest_framework import serializers
from django.contrib.auth import get_user_model

from user.models import User
from .models import Chat, Message


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for displaying user info in messages and chats
    """

    class Meta:
        model = User
        fields = ['uid', 'name', 'email', 'photo', 'role']


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender = UserBasicSerializer(read_only=True)
    receiver = UserBasicSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['uid', 'sender', 'receiver', 'content', 'is_read', 'created_at', 'updated_at']
        read_only_fields = ['uid', 'sender', 'receiver', 'created_at', 'updated_at']


class SendMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for sending messages
    """
    receiver_uid = serializers.UUIDField(write_only=True)

    class Meta:
        model = Message
        fields = ['receiver_uid', 'content']

    def validate_receiver_uid(self, value):
        try:
            receiver = User.objects.get(uid=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Receiver not found")

        # Check if trying to send message to self
        request = self.context.get('request')
        if request and request.user.uid == value:
            raise serializers.ValidationError("Cannot send message to yourself")

        return value

    def create(self, validated_data):
        request = self.context.get('request')
        sender = request.user
        receiver_uid = validated_data.pop('receiver_uid')
        receiver = User.objects.get(uid=receiver_uid)

        # Get or create chat between users
        chat, created = Chat.get_or_create_chat(sender, receiver)

        # Create message
        message = Message.objects.create(
            chat=chat,
            sender=sender,
            receiver=receiver,
            **validated_data
        )

        return message


class ChatSerializer(serializers.ModelSerializer):
    """
    Serializer for Chat model
    """
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = ['uid', 'other_user', 'last_message', 'unread_count', 'created_at', 'updated_at']

    def get_other_user(self, obj):
        request = self.context.get('request')
        if request:
            other_user = obj.get_other_user(request.user)
            return UserBasicSerializer(other_user).data
        return None

    def get_last_message(self, obj):
        last_message = obj.messages.first()  # Since messages are ordered by -created_at
        if last_message:
            return {
                'uid': last_message.uid,
                'content': last_message.content,
                'sender_name': last_message.sender.name,
                'created_at': last_message.created_at,
                'is_read': last_message.is_read
            }
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request:
            return obj.messages.filter(receiver=request.user, is_read=False).count()
        return 0