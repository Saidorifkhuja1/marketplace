from django.db import transaction
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
import logging

from .models import User, UserLoginHistory
from .serializers import (
    TelegramAuthSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordResetSerializer,
    LoginHistorySerializer
)
from .telegram_auth import verify_telegram_auth, get_client_ip

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_auth_view(request):
    """
    Telegram Web App authentication endpoint
    User avtomatik register yoki login qiladi
    """
    try:
        serializer = TelegramAuthSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        auth_data = serializer.validated_data.copy()

        # Telegram ma'lumotlarini tekshirish
        if not verify_telegram_auth(auth_data):
            logger.warning(f"Invalid Telegram auth attempt for ID: {auth_data.get('id')}")
            return Response(
                {'error': 'Invalid Telegram authentication'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        telegram_id = auth_data['id']

        with transaction.atomic():
            # User mavjudligini tekshirish
            user, created = User.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'name': f"{auth_data.get('first_name', '')} {auth_data.get('last_name', '')}".strip(),
                    'username': auth_data.get('username', ''),
                }
            )

            # Agar user o'chirilgan bo'lsa, qayta tiklash
            if user.is_deleted:
                user.restore()

            # Last login vaqtini yangilash
            user.last_login_at = timezone.now()
            user.save()

            # Login history yozish
            UserLoginHistory.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )

            # JWT token yaratish
            refresh = RefreshToken.for_user(user)

            logger.info(f"User {'created' if created else 'logged in'}: {user.telegram_id}")

            return Response({
                'success': True,
                'created': created,
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }
            }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Telegram auth error: {str(e)}")
        return Response(
            {'error': 'Authentication failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def token_verify_view(request):
    """Token verification endpoint"""
    return Response({
        'valid': True,
        'user': UserProfileSerializer(request.user).data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def token_refresh_view(request):
    """Token refresh endpoint"""
    try:
        refresh = RefreshToken.for_user(request.user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        })
    except Exception as e:
        return Response(
            {'error': 'Token refresh failed'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = UserUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(UserProfileSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """Password change endpoint"""
    serializer = PasswordResetSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user

        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'error': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({'success': True, 'message': 'Password changed successfully'})

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account_view(request):
    """Account soft delete endpoint"""
    user = request.user
    user.soft_delete()
    logger.info(f"User account soft deleted: {user.telegram_id}")
    return Response({'success': True, 'message': 'Account deleted successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def login_history_view(request):
    """User login history"""
    history = UserLoginHistory.objects.filter(user=request.user)[:20]
    serializer = LoginHistorySerializer(history, many=True)
    return Response(serializer.data)

