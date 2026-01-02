"""
Custom authentication backends for SPAS.

Implements email-based authentication with additional security features.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from .throttling import SuspiciousActivityDetector
from .signals import suspicious_activity_detected
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that uses email instead of username.
    Includes lockout protection and activity logging.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user with email and password.

        Args:
            request: HttpRequest object
            username: Email address (we use email as username)
            password: User password
            **kwargs: Additional keyword arguments

        Returns:
            User object if authentication successful, None otherwise
        """
        if username is None or password is None:
            return None

        # Check if account is locked out
        is_locked, remaining_time = SuspiciousActivityDetector.is_locked_out(username)
        if is_locked:
            logger.warning(
                f"Login attempt for locked account: {username}. "
                f"Remaining time: {remaining_time}s"
            )
            # Send signal for suspicious activity
            suspicious_activity_detected.send(
                sender=self.__class__,
                user=username,
                activity_type='locked_account_access_attempt',
                request=request
            )
            return None

        try:
            # Try to get user by email (case-insensitive)
            user = User.objects.get(
                Q(email__iexact=username) | Q(email=username)
            )
        except User.DoesNotExist:
            # Run password hasher to prevent timing attacks
            User().set_password(password)
            return None
        except User.MultipleObjectsReturned:
            logger.error(f"Multiple users found with email: {username}")
            return None

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Login attempt for inactive account: {username}")
            return None

        # Verify password
        if user.check_password(password):
            # Password is correct - clear failed attempts
            SuspiciousActivityDetector.record_successful_login(username)
            return user
        else:
            # Password is incorrect - record failed attempt
            ip_address = self._get_ip_address(request)
            attempt_info = SuspiciousActivityDetector.record_failed_login(
                username, ip_address
            )

            if attempt_info['locked']:
                # Account has been locked
                suspicious_activity_detected.send(
                    sender=self.__class__,
                    user=username,
                    activity_type='account_locked_brute_force',
                    request=request
                )

            return None

    def get_user(self, user_id):
        """
        Get user by ID.

        Args:
            user_id: User's ID

        Returns:
            User object if found, None otherwise
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _get_ip_address(self, request):
        """
        Extract IP address from request.

        Args:
            request: HttpRequest object

        Returns:
            str: IP address
        """
        if not request:
            return 'unknown'

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'unknown')
        return ip


class TokenAuthBackend(ModelBackend):
    """
    Backend for token-based authentication (JWT).
    Used in conjunction with rest_framework_simplejwt.
    """

    def authenticate(self, request, token=None, **kwargs):
        """
        Authenticate using JWT token.

        This is primarily handled by simplejwt middleware,
        but we can add custom logic here if needed.

        Args:
            request: HttpRequest object
            token: JWT token
            **kwargs: Additional keyword arguments

        Returns:
            User object if valid, None otherwise
        """
        # This is typically handled by simplejwt
        # We can add custom validation logic here if needed
        return None


class AdminOnlyBackend(ModelBackend):
    """
    Authentication backend that only allows admin users.
    Useful for admin panel access restriction.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate admin users only.

        Args:
            request: HttpRequest object
            username: Email address
            password: User password
            **kwargs: Additional keyword arguments

        Returns:
            User object if admin and authentication successful, None otherwise
        """
        user = super().authenticate(request, username, password, **kwargs)

        if user and (user.is_superuser or user.is_staff or user.is_admin()):
            return user

        return None
