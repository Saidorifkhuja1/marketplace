from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404
from .models import Chat, Message
from .serializers import (
    MessageSerializer,
    SendMessageSerializer,
    ChatSerializer
)


class SendMessageView(generics.CreateAPIView):
    """
    API to send a message to another user
    POST /api/messages/send/
    Body: {
        "receiver_uid": "uuid-of-receiver",
        "content": "message content"
    }
    """
    serializer_class = SendMessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        # Return the created message with full details
        response_serializer = MessageSerializer(message)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class MyMessagesListView(generics.ListAPIView):
    """
    API to get messages received by the current user
    GET /api/messages/my-messages/
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(receiver=self.request.user)


class ChatListView(generics.ListAPIView):
    """
    API to get all chats of the current user
    GET /api/messages/chats/
    """
    serializer_class = ChatSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Chat.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).annotate(
            last_message_time=Max('messages__created_at')
        ).order_by('-last_message_time')


class ChatMessagesView(generics.ListAPIView):
    """
    API to get all messages in a specific chat
    GET /api/messages/chats/{chat_uid}/messages/
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chat_uid = self.kwargs['chat_uid']
        chat = get_object_or_404(Chat, uid=chat_uid)

        # Verify user is part of this chat
        user = self.request.user
        if chat.user1 != user and chat.user2 != user:
            return Message.objects.none()

        return chat.messages.all()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Mark messages as read when user views the chat
        chat_uid = self.kwargs['chat_uid']
        chat = get_object_or_404(Chat, uid=chat_uid)

        # Mark unread messages as read for the current user
        Message.objects.filter(
            chat=chat,
            receiver=request.user,
            is_read=False
        ).update(is_read=True)

        return response


class SentMessagesView(generics.ListAPIView):
    """
    API to get messages sent by the current user
    GET /api/messages/sent/
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)


class AllMessagesView(generics.ListAPIView):
    """
    API to get all messages (sent and received) by the current user
    GET /api/messages/all/
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        )