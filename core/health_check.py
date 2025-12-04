from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Health check endpoint for monitoring
    Returns status of database and cache
    """
    health_status = {
        'status': 'healthy',
        'database': 'unknown',
        'cache': 'unknown',
    }

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        health_status['database'] = 'ok'
    except Exception as e:
        health_status['database'] = 'error'
        health_status['status'] = 'unhealthy'
        logger.error(f"Database health check failed: {e}")

    # Check cache
    try:
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['cache'] = 'ok'
        else:
            health_status['cache'] = 'error'
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['cache'] = 'error'
        logger.warning(f"Cache health check failed: {e}")

    status_code = 200 if health_status['status'] == 'healthy' else 503

    return JsonResponse(health_status, status=status_code)
