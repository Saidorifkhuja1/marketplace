from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
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

@api_view(['POST'])
def register_user(request):
    telegram_id = request.data.get('telegram_id')
    name = request.data.get('name')
    auth_hash = request.data.get('auth_hash')

    if not telegram_id or not name or not auth_hash:
        return Response({'error': 'Missing required fields'}, status=400)

    # Verify auth hash
    bot_secret = "AAHpm29cZv5TDRT8GBEx9REo2J26N7_8yVs".split(":")[1]  # Secret part
    expected_hash = hmac.new(
        bot_secret.encode(),
        f"{telegram_id}:{name}".encode(),
        hashlib.sha256
    ).hexdigest()

    if auth_hash != expected_hash:
        return Response({'error': 'Invalid authentication'}, status=401)

    # Create or get user


    user, created = User.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'name': name,
            'email': f"{telegram_id}@telegram.local",  # Fake unique email
            'phone_number': f"+99899{str(telegram_id)[-7:]}",  # Dummy phone
            'is_active': True
        }
    )

    # Generate JWT token
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    return Response({
        'jwt_token': access_token,
        'refresh_token': str(refresh),
        'user_id': str(user.uid),
        'message': 'User registered successfully'
    })

class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "uid"

    def get_queryset(self):
        decoded_token = unhash_token(self.request.headers)
        user_id = decoded_token.get('user_id')
        return User.objects.filter(uid=user_id)


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

