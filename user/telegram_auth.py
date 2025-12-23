import hashlib
import hmac
from django.conf import settings
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def verify_telegram_auth(auth_data):
    """
    Telegram WebApp authentication verification
    phone_number is excluded from hash calculation as it's not part of Telegram's auth data
    """
    try:
        # Make a copy to avoid modifying the original
        data_to_verify = auth_data.copy()

        # Extract hash from the data
        received_hash = data_to_verify.pop('hash', None)
        if not received_hash:
            logger.warning("No hash provided in auth_data")
            return False

        logger.info(f"Received hash: {received_hash}")

        # Remove phone_number from hash verification (it's not part of Telegram's hash)
        phone_number = data_to_verify.pop('phone_number', None)
        logger.info(f"Phone number (excluded from hash): {phone_number}")

        # Verify auth_date (should not be older than 24 hours)
        auth_date = data_to_verify.get('auth_date')
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

        # Filter out empty or None values
        filtered_data = {k: v for k, v in data_to_verify.items() if v != '' and v is not None}

        logger.info(f"Filtered data for hash: {filtered_data}")

        # Create data check string (sorted by key)
        data_check_string = '\n'.join([
            f"{key}={value}"
            for key, value in sorted(filtered_data.items())
        ])

        logger.info(f"Data check string: {data_check_string}")

        # Create secret key
        secret_key = hmac.new(
            key="WebAppData".encode(),
            msg=settings.TELEGRAM_BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()

        # Calculate hash
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        logger.info(f"Calculated hash: {calculated_hash}")
        logger.info(f"Received hash:   {received_hash}")

        # Compare hashes
        is_valid = hmac.compare_digest(calculated_hash, received_hash)
        logger.info(f"Hash match: {is_valid}")

        return is_valid

    except Exception as e:
        logger.error(f"Telegram auth verification error: {e}", exc_info=True)
        return False


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

