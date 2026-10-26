import time
import logging
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Simple rate limiting middleware.
    Limits requests per IP address.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.RATE_LIMIT_PER_MINUTE = 60  # Requests per minute
        self.RATE_LIMIT_WINDOW = 60  # Seconds

    def __call__(self, request):
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Check rate limit only for API endpoints
        if request.path.startswith('/api/'):
            cache_key = f"rate_limit:{ip}"
            request_count = cache.get(cache_key, 0)

            if request_count >= self.RATE_LIMIT_PER_MINUTE:
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                return JsonResponse(
                    {
                        "error": "Rate limit exceeded. Maximum 60 requests per minute.",
                        "retry_after": self.RATE_LIMIT_WINDOW
                    },
                    status=429
                )

            # Increment counter
            cache.set(cache_key, request_count + 1, self.RATE_LIMIT_WINDOW)

        response = self.get_response(request)
        return response


class RequestLoggingMiddleware:
    """Log all API requests and responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time

        # Log API requests
        if request.path.startswith('/api/'):
            logger.info(
                f"{request.method} {request.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.3f}s | "
                f"IP: {self._get_client_ip(request)}"
            )

        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', 'UNKNOWN')
