"""
Custom middleware for security and auditing.
"""
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
import logging

from .models import AuditLog
from .utils import get_client_ip

logger = logging.getLogger(__name__)


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware to automatically audit certain requests.

    This logs all non-GET requests and failed authentication attempts.
    """

    # Endpoints to skip auditing
    SKIP_AUDIT_ENDPOINTS = [
        '/api/schema/',
        '/api/docs/',
        '/static/',
        '/media/',
        '/admin/jsi18n/',
    ]

    def should_audit(self, request):
        """Determine if the request should be audited."""
        path = request.path

        # Skip certain endpoints
        for skip_path in self.SKIP_AUDIT_ENDPOINTS:
            if path.startswith(skip_path):
                return False

        # Audit non-GET requests
        if request.method not in ['GET', 'HEAD', 'OPTIONS']:
            return True

        return False

    def process_response(self, request, response):
        """Process the response and create audit logs if needed."""
        if not self.should_audit(request):
            return response

        # Only audit if user is authenticated or if it's a failed auth attempt
        if not request.user.is_authenticated and response.status_code != 401:
            return response

        # Determine action type
        action = None
        if request.method == 'POST':
            action = AuditLog.Action.CREATE
        elif request.method in ['PUT', 'PATCH']:
            action = AuditLog.Action.UPDATE
        elif request.method == 'DELETE':
            action = AuditLog.Action.DELETE

        # Log failed authentication attempts
        if response.status_code == 401:
            action = AuditLog.Action.PERMISSION_DENIED

        if action:
            try:
                AuditLog.log_action(
                    user=request.user if request.user.is_authenticated else None,
                    action=action,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                )
            except Exception as e:
                logger.error(f"Failed to create audit log: {e}")

        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """

    def process_response(self, request, response):
        """Add security headers to the response."""
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'

        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'

        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'

        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Content Security Policy
        response['Content-Security-Policy'] = "default-src 'self'"

        # Permissions Policy (formerly Feature-Policy)
        response['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware based on IP address.

    This is a fallback in case DRF throttling is not configured.
    """

    # Maximum requests per minute per IP
    MAX_REQUESTS_PER_MINUTE = 60

    def process_request(self, request):
        """Check if the IP address has exceeded the rate limit."""
        # Skip rate limiting for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None

        ip_address = get_client_ip(request)
        cache_key = f'rate_limit_{ip_address}'

        # Get current request count
        request_count = cache.get(cache_key, 0)

        if request_count >= self.MAX_REQUESTS_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")

            # Log the rate limit violation
            try:
                AuditLog.log_action(
                    user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                    action=AuditLog.Action.ERROR,
                    ip_address=ip_address,
                    endpoint=request.path,
                    method=request.method,
                    extra_data={'error': 'Rate limit exceeded'}
                )
            except Exception as e:
                logger.error(f"Failed to log rate limit violation: {e}")

            return JsonResponse(
                {'error': 'Trop de requêtes. Veuillez réessayer plus tard.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Increment request count
        cache.set(cache_key, request_count + 1, 60)  # 60 seconds

        return None


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all requests and responses.

    Useful for debugging and monitoring.
    """

    # Endpoints to skip logging
    SKIP_LOG_ENDPOINTS = [
        '/admin/jsi18n/',
        '/static/',
        '/media/',
    ]

    def process_request(self, request):
        """Log incoming request."""
        # Skip certain endpoints
        for skip_path in self.SKIP_LOG_ENDPOINTS:
            if request.path.startswith(skip_path):
                return None

        logger.debug(
            f"Request: {request.method} {request.path} "
            f"from {get_client_ip(request)} "
            f"User: {request.user if hasattr(request, 'user') else 'Anonymous'}"
        )

        return None

    def process_response(self, request, response):
        """Log response."""
        # Skip certain endpoints
        for skip_path in self.SKIP_LOG_ENDPOINTS:
            if request.path.startswith(skip_path):
                return response

        logger.debug(
            f"Response: {request.method} {request.path} "
            f"Status: {response.status_code}"
        )

        return response


class PermissionDeniedLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log permission denied events.

    This helps identify potential security issues or misconfigured permissions.
    """

    def process_response(self, request, response):
        """Log permission denied responses."""
        if response.status_code in [401, 403]:
            try:
                AuditLog.log_action(
                    user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                    action=AuditLog.Action.PERMISSION_DENIED,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    endpoint=request.path,
                    method=request.method,
                    status_code=response.status_code,
                    extra_data={
                        'user_role': request.user.role if hasattr(request, 'user') and request.user.is_authenticated else None
                    }
                )
            except Exception as e:
                logger.error(f"Failed to log permission denied: {e}")

        return response
