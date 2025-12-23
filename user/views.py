from django.db import transaction, IntegrityError
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User, UserLoginHistory
from .serializers import (
    TelegramAuthSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordResetSerializer,
    LoginHistorySerializer,
    LoginSerializer
)
from .telegram_auth import verify_telegram_auth, get_client_ip

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_auth_view(request):
    """
    Telegram Web App authentication endpoint with phone number
    User automatically registers or logs in
    """
    logger.info(f"Received auth request: {request.data}")

    serializer = TelegramAuthSerializer(data=request.data)
    if not serializer.is_valid():
        logger.error(f"Invalid data: {serializer.errors}")
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Get validated data - DO NOT MODIFY IT before verification
    auth_data = serializer.validated_data.copy()

    logger.info(f"Validated auth data: {auth_data}")

    # 1️⃣ Verify Telegram authentication
    if not verify_telegram_auth(auth_data):
        logger.warning(f"Invalid Telegram auth attempt for ID: {auth_data.get('id')}")
        return Response(
            {'error': 'Invalid Telegram authentication'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # 2️⃣ Extract data after successful verification
    telegram_id = auth_data['id']
    phone_number = auth_data.get('phone_number', '')

    # 3️⃣ Format phone number (+998 prefix if not present)
    if phone_number and not phone_number.startswith('+'):
        phone_number = f"+{phone_number}"

    logger.info(f"Processing auth for telegram_id: {telegram_id}, phone: {phone_number}")

    # 4️⃣ Create unique email for Telegram user
    email = f"telegram_{telegram_id}@telegram.local"

    # 5️⃣ Create safe name
    name = (
            f"{auth_data.get('first_name', '')} {auth_data.get('last_name', '')}".strip()
            or auth_data.get('username')
            or "Telegram User"
    )

    username = auth_data.get('username', '')

    try:
        with transaction.atomic():
            # 6️⃣ Get or create user (by telegram_id)
            user, created = User.objects.get_or_create(
                telegram_id=telegram_id,
                defaults={
                    'email': email,
                    'name': name,
                    'username': username,
                    'phone_number': phone_number if phone_number else None,
                    'is_active': True,
                    'role': 'client',
                }
            )

            # 7️⃣ Update phone number if user exists and phone is new
            if not created and phone_number:
                if user.phone_number != phone_number:
                    user.phone_number = phone_number
                    user.save(update_fields=['phone_number'])
                    logger.info(f"Updated phone number for user {telegram_id}")

            # 8️⃣ Restore user if soft-deleted
            if user.is_deleted:
                user.restore()
                logger.info(f"Restored deleted user {telegram_id}")

            # 9️⃣ Update last login time
            user.last_login_at = timezone.now()
            user.save(update_fields=['last_login_at'])

            # 🔟 Log login history
            UserLoginHistory.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=True
            )

            # 1️⃣1️⃣ Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            logger.info(
                f"Telegram user {'created' if created else 'logged in'}: {telegram_id}, phone: {phone_number}"
            )

            return Response(
                {
                    'success': True,
                    'created': created,
                    'user': UserProfileSerializer(user).data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                    }
                },
                status=status.HTTP_200_OK
            )

    except IntegrityError as e:
        logger.error(f"Telegram auth DB error: {str(e)}")

        # If phone number already exists with another account
        if 'phone_number' in str(e):
            return Response(
                {'error': 'This phone number is already registered with another account'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'error': 'User creation failed', 'details': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        logger.error(f"Telegram auth error: {str(e)}", exc_info=True)
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


@swagger_auto_schema(
    method='post',
    request_body=LoginSerializer,
    responses={
        200: openapi.Response(
            description='Login successful',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'user': openapi.Schema(type=openapi.TYPE_OBJECT),
                    'tokens': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'access': openapi.Schema(type=openapi.TYPE_STRING),
                            'refresh': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        ),
        401: openapi.Response(description='Invalid credentials'),
        400: openapi.Response(description='Invalid data'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Email and password login endpoint
    Returns JWT tokens for authenticated user
    """
    try:
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'error': 'Invalid data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt with inactive user: {email}")
            return Response(
                {'error': 'User account is inactive'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check if user is deleted
        if user.is_deleted:
            logger.warning(f"Login attempt with deleted user: {email}")
            return Response(
                {'error': 'User account has been deleted'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verify password
        if not user.check_password(password):
            logger.warning(f"Invalid password attempt for user: {email}")
            # Log failed login attempt
            UserLoginHistory.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                success=False
            )
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Update last login time
        user.last_login_at = timezone.now()
        user.save()

        # Log successful login
        UserLoginHistory.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        logger.info(f"User logged in successfully: {email}")

        return Response({
            'success': True,
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response(
            {'error': 'Login failed', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


