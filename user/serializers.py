from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, UserLoginHistory


class TelegramAuthSerializer(serializers.Serializer):
    """Telegram Web App authentication serializer with phone number"""
    id = serializers.IntegerField()
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)
    photo_url = serializers.URLField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=True)  # Telefon raqami majburiy
    auth_date = serializers.IntegerField()
    hash = serializers.CharField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('telegram_id', 'name', 'username', 'phone_number', 'email', 'photo', 'role')
        read_only_fields = ('uid',)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'username', 'phone_number', 'email', 'photo', 'role')
        read_only_fields = ('uid', 'telegram_id')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'uid',
            'name',
            'username',
            'phone_number',
            'email',
            'telegram_id',
            'photo',
            'role',
            'is_active',
            'created_at',
            'last_login_at'
        )
        read_only_fields = ('uid', 'telegram_id', 'is_active', 'created_at')


class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class LoginHistorySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = UserLoginHistory
        fields = ('id', 'user', 'user_name', 'login_time', 'ip_address', 'user_agent', 'success')
        read_only_fields = ('id', 'user', 'login_time')


class LoginSerializer(serializers.Serializer):
    """Email and password login serializer"""
    email = serializers.EmailField(help_text="User email address")
    password = serializers.CharField(write_only=True, help_text="User password")


