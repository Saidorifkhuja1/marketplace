import hashlib
import hmac
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


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
            logger.warning("No hash provided in auth_data")
            return False

        logger.info(f"Received hash: {received_hash}")
        logger.info(f"Auth data (without hash): {auth_data}")

        # auth_date ni tekshirish (24 soatdan eski bo'lmasligi kerak)
        auth_date = auth_data.get('auth_date')
        if auth_date:
            try:
                auth_time = datetime.fromtimestamp(int(auth_date))
                time_diff = datetime.now() - auth_time
                logger.info(f"Auth time: {auth_time}, Time diff: {time_diff}")

                if time_diff > timedelta(hours=24):
                    logger.warning(f"Auth data is too old: {time_diff}")
                    return False
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid auth_date: {auth_date}, error: {e}")
                return False

        # Data stringini yaratish (MUHIM: faqat bo'sh bo'lmagan qiymatlar)
        # Bo'sh stringlarni olib tashlash
        filtered_data = {k: v for k, v in auth_data.items() if v != '' and v is not None}

        data_check_string = '\n'.join([
            f"{key}={value}"
            for key, value in sorted(filtered_data.items())
        ])

        logger.info(f"Data check string: {data_check_string}")

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

        logger.info(f"Calculated hash: {calculated_hash}")
        logger.info(f"Hash match: {hmac.compare_digest(calculated_hash, received_hash)}")

        # Hashlarni solishtirish
        return hmac.compare_digest(calculated_hash, received_hash)

    except Exception as e:
        logger.error(f"Telegram auth verification error: {e}", exc_info=True)
        return False


def get_client_ip(request):
    """Request dan client IP manzilini olish"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip