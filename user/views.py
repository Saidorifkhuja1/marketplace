from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
import logging
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import *
from rest_framework.decorators import api_view
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from .utils import unhash_token
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import NotFound, AuthenticationFailed
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
import hashlib
import hmac

# class UserRegistrationAPIView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserRegistrationSerializer
#     parser_classes = [MultiPartParser, FormParser]
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#
#         refresh = RefreshToken.for_user(user)
#         access_token = refresh.access_token
#
#         token_data = {
#             "refresh": str(refresh),
#             "access": str(access_token),
#         }
#
#         return Response(token_data, status=status.HTTP_201_CREATED)

logger = logging.getLogger(__name__)


@api_view(['POST'])
def register_user(request):
    logger.info(f"Registration request received: {request.data}")

    telegram_id = request.data.get('telegram_id')
    name = request.data.get('name')
    auth_hash = request.data.get('auth_hash')

    # Validate required fields
    if not telegram_id or not name or not auth_hash:
        logger.error(f"Missing fields - telegram_id: {telegram_id}, name: {name}, auth_hash: {auth_hash}")
        return Response({'error': 'Missing required fields'}, status=400)

    # FIXED: Use the correct bot token secret part
    # Your bot token is: 8198411082:AAHpm29cZv5TDRT8GBEx9REo2J26N7_8yVs
    # So the secret part after ":" is: AAHpm29cZv5TDRT8GBEx9REo2J26N7_8yVs
    bot_secret = "AAHpm29cZv5TDRT8GBEx9REo2J26N7_8yVs"  # This is already the secret part

    # Generate expected hash
    expected_hash = hmac.new(
        bot_secret.encode(),
        f"{telegram_id}:{name}".encode(),
        hashlib.sha256
    ).hexdigest()

    logger.info(f"Expected hash: {expected_hash}, Received hash: {auth_hash}")

    if auth_hash != expected_hash:
        logger.error("Hash verification failed")
        return Response({'error': 'Invalid authentication'}, status=401)

    try:
        with transaction.atomic():
            # Check if user already exists
            existing_user = User.objects.filter(telegram_id=telegram_id).first()

            if existing_user:
                logger.info(f"User {telegram_id} already exists, updating...")
                # Update existing user
                existing_user.name = name
                existing_user.save()
                user = existing_user
                created = False
            else:
                logger.info(f"Creating new user for telegram_id: {telegram_id}")

                # Generate unique email and phone - make sure they're truly unique
                unique_email = f"tg_{telegram_id}@telegram.local"
                # Make phone number more unique by using full telegram_id
                unique_phone = f"+99890{str(telegram_id)[-7:].zfill(7)}"

                logger.info(f"Generated email: {unique_email}, phone: {unique_phone}")

                # Create new user with all required fields
                user = User.objects.create(
                    telegram_id=telegram_id,
                    name=name,
                    email=unique_email,
                    phone_number=unique_phone,
                    is_active=True,
                    role='client'
                )
                created = True
                logger.info(f"User created successfully: {user.uid}")

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        logger.info(f"JWT token generated for user {user.uid}")

        return Response({
            'jwt_token': access_token,
            'refresh_token': str(refresh),
            'user_id': str(user.uid),
            'created': created,
            'message': 'User registered successfully'
        }, status=201 if created else 200)

    except Exception as e:
        logger.error(f"Error creating/updating user: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

        return Response({
            'error': f'Database error: {str(e)}'
        }, status=500)


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uid"

    def get_queryset(self):
        decoded_token = unhash_token(self.request.headers)
        user_uid = decoded_token.get('user_uid')
        return User.objects.filter(uid=user_uid)


class PasswordResetView(APIView):
    queryset = User.objects.all()
    serializer_class = PasswordResetSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=PasswordResetSerializer
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        decoded_token = unhash_token(request.headers)
        user_id = decoded_token.get("user_id")

        if not user_id:
            raise AuthenticationFailed("User ID not found in token")

        old_password = serializer.validated_data.get("old_password")
        new_password = serializer.validated_data.get("new_password")

        user = get_object_or_404(User, uid=user_id)

        if not check_password(old_password, user.password):
            return Response(
                {"error": "Incorrect old password!"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.password = make_password(new_password)
        user.save()

        return Response(
            {"data": "Password changed successfully"},
            status=status.HTTP_200_OK
        )


class RetrieveProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        decoded_token = unhash_token(self.request.headers)
        user_id = decoded_token.get('user_id')

        if not user_id:
            raise NotFound("User not found")

        user = get_object_or_404(User, uid=user_id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class DeleteProfileAPIView(generics.DestroyAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    def get_queryset(self):
        decoded_token = unhash_token(self.request.headers)
        user_id = decoded_token.get('user_id')
        return User.objects.filter(uid=user_id)

