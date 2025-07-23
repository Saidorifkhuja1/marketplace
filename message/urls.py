from django.urls import path
from .views import *

app_name = 'messages'

urlpatterns = [
    # Send message
    path('send/', SendMessageView.as_view()),

    # Get received messages
    path('my-messages/', MyMessagesListView.as_view()),

    # Get all chats
    path('chats/', ChatListView.as_view()),

    # Get messages in a specific chat
    path('chats/<uuid:chat_uid>/messages/', ChatMessagesView.as_view()),

    # Get sent messages
    path('sent/', SentMessagesView.as_view()),

    # Get all messages (sent and received)
    path('all/', AllMessagesView.as_view()),
]