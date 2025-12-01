import hashlib
import hmac
from django.conf import settings
from datetime import datetime, timedelta


def verify_telegram_auth(auth_data):
    """
    Telegram Web App authentication ma'lumotlarini tekshiradi

    Args:
        auth_data (dict): Telegram dan kelgan auth ma'lumotlari

    Returns:
        bool: Ma'lumotlar to'g'ri bo'lsa True, aks holda False
    """
    try:
        # Hash ni olish va auth_data dan o'chirish
        received_hash = auth_data.pop('hash', None)
        if not received_hash:
            return False

        # auth_date ni tekshirish (24 soatdan eski bo'lmasligi kerak)
        auth_date = auth_data.get('auth_date')
        if auth_date:
            auth_time = datetime.fromtimestamp(int(auth_date))
            if datetime.now() - auth_time > timedelta(hours=24):
                return False

        # Data stringini yaratish
        data_check_string = '\n'.join([
            f"{key}={value}"
            for key, value in sorted(auth_data.items())
        ])

        # Secret key yaratish
        secret_key = hmac.new(
            key="WebAppData".encode(),
            msg=settings.TELEGRAM_BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()

        # Hash yaratish
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        # Hashlarni solishtirish
        return hmac.compare_digest(calculated_hash, received_hash)

    except Exception as e:
        print(f"Telegram auth verification error: {e}")
        return False


def get_client_ip(request):
    """Request dan client IP manzilini olish"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
