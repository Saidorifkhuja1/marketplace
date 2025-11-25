from django.contrib import admin
from .models import Chat, Message


# @admin.register(Chat)
# class ChatAdmin(admin.ModelAdmin):
#     list_display = ['uid', 'user1', 'user2', 'created_at', 'updated_at']
#     list_filter = ['created_at', 'updated_at']
#     search_fields = ['user1__name', 'user1__email', 'user2__name', 'user2__email']
#     readonly_fields = ['uid', 'created_at', 'updated_at']
#     raw_id_fields = ['user1', 'user2']
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('user1', 'user2')
#
#
# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ['uid', 'sender', 'receiver', 'content_preview', 'is_read', 'created_at']
#     list_filter = ['is_read', 'created_at', 'updated_at']
#     search_fields = ['sender__name', 'sender__email', 'receiver__name', 'receiver__email', 'content']
#     readonly_fields = ['uid', 'created_at', 'updated_at']
#     raw_id_fields = ['chat', 'sender', 'receiver']
#
#     def content_preview(self, obj):
#         """Show first 50 characters of message content"""
#         return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
#
#     content_preview.short_description = 'Content Preview'
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('sender', 'receiver', 'chat')
#
#

