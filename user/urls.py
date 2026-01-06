from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('auth/telegram/', views.telegram_auth_view, name='telegram-auth'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/verify/', views.token_verify_view, name='token-verify'),
    path('auth/refresh/', views.token_refresh_view, name='token-refresh'),
    path("auth/telegram/token/", views.TelegramTokenObtainView.as_view(), name="telegram-token"),

    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/change-password/', views.change_password_view, name='change-password'),
    path('profile/delete/', views.delete_account_view, name='delete-account'),

    # Login History
    path('profile/login-history/', views.login_history_view, name='login-history'),
]



