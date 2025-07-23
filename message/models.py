import uuid
from django.db import models
from django.contrib.auth import get_user_model

from user.models import User


class Chat(models.Model):
    """
    Represents a unique conversation between two users
    """
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure unique chat between two users regardless of order
        constraints = [
            models.UniqueConstraint(
                fields=['user1', 'user2'],
                name='unique_chat_users'
            )
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"Chat between {self.user1.name} and {self.user2.name}"

    @classmethod
    def get_or_create_chat(cls, user1, user2):
        """
        Get or create a chat between two users, ensuring user1.id < user2.id for consistency
        """
        if user1.uid == user2.uid:
            raise ValueError("Cannot create chat with yourself")

        # Ensure consistent ordering (smaller uid first)
        if user1.uid > user2.uid:
            user1, user2 = user2, user1

        chat, created = cls.objects.get_or_create(
            user1=user1,
            user2=user2
        )
        return chat, created

    def get_other_user(self, current_user):
        """
        Get the other user in the chat
        """
        if self.user1 == current_user:
            return self.user2
        elif self.user2 == current_user:
            return self.user1
        else:
            raise ValueError("User is not part of this chat")


class Message(models.Model):
    """
    Represents a message in a chat
    """
    uid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.sender.name} to {self.receiver.name}"

    def save(self, *args, **kwargs):
        # Update chat's updated_at when a new message is saved
        super().save(*args, **kwargs)
        self.chat.save()  # This will trigger the auto_now on updated_at