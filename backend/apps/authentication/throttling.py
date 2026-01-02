"""
Custom throttling classes for authentication endpoints.

Implements rate limiting to prevent brute force attacks and abuse.
"""
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class LoginRateThrottle(AnonRateThrottle):
    """
    Throttle for login attempts.
    Limits login attempts to prevent brute force attacks.
    """
    scope = 'login'
    rate = '5/min'  # 5 attempts per minute

    def get_cache_key(self, request, view):
        """
        Use IP address and email combination for more accurate throttling.
        """
        if request.user.is_authenticated:
            return None  # Don't throttle authenticated users

        # Get IP address
        ident = self.get_ident(request)

        # Get email from request data
        email = request.data.get('email', '')

        # Create composite key
        if email:
            cache_key = f'throttle_login_{ident}_{email}'
        else:
            cache_key = f'throttle_login_{ident}'

        return self.cache_format % {
            'scope': self.scope,
            'ident': cache_key
        }


class PasswordResetRateThrottle(AnonRateThrottle):
    """
    Throttle for password reset requests.
    Prevents abuse of password reset functionality.
    """
    scope = 'password_reset'
    rate = '3/hour'  # 3 attempts per hour


class RegisterRateThrottle(AnonRateThrottle):
    """
    Throttle for registration attempts.
    Prevents mass account creation.
    """
    scope = 'register'
    rate = '3/day'  # 3 registrations per day per IP


class EmailVerificationRateThrottle(AnonRateThrottle):
    """
    Throttle for email verification resend requests.
    """
    scope = 'email_verification'
    rate = '3/hour'  # 3 verification emails per hour


class TokenRefreshRateThrottle(UserRateThrottle):
    """
    Throttle for token refresh requests.
    """
    scope = 'token_refresh'
    rate = '30/hour'  # 30 refreshes per hour


class SuspiciousActivityDetector:
    """
    Detects and logs suspicious authentication activities.
    """

    FAILED_LOGIN_THRESHOLD = 5  # Number of failed attempts before flagging
    FAILED_LOGIN_WINDOW = 300  # Time window in seconds (5 minutes)
    LOCKOUT_DURATION = 900  # Lockout duration in seconds (15 minutes)

    @classmethod
    def get_cache_key(cls, identifier, activity_type='login'):
        """Generate cache key for tracking attempts."""
        return f'suspicious_{activity_type}_{identifier}'

    @classmethod
    def get_lockout_key(cls, identifier):
        """Generate cache key for account lockout."""
        return f'lockout_{identifier}'

    @classmethod
    def record_failed_login(cls, email, ip_address):
        """
        Record a failed login attempt.

        Args:
            email: User's email address
            ip_address: IP address of the request

        Returns:
            dict: Status information about the attempt
        """
        # Check if already locked out
        lockout_key = cls.get_lockout_key(email)
        if cache.get(lockout_key):
            remaining_time = cache.ttl(lockout_key)
            logger.warning(
                f"Login attempt for locked account: {email} from {ip_address}. "
                f"Remaining lockout: {remaining_time}s"
            )
            return {
                'locked': True,
                'remaining_time': remaining_time,
                'attempts': cls.FAILED_LOGIN_THRESHOLD
            }

        # Track failed attempts
        cache_key = cls.get_cache_key(email)
        attempts = cache.get(cache_key, 0) + 1
        cache.set(cache_key, attempts, cls.FAILED_LOGIN_WINDOW)

        logger.warning(
            f"Failed login attempt {attempts}/{cls.FAILED_LOGIN_THRESHOLD} "
            f"for {email} from {ip_address}"
        )

        # Lock account if threshold exceeded
        if attempts >= cls.FAILED_LOGIN_THRESHOLD:
            cache.set(lockout_key, True, cls.LOCKOUT_DURATION)
            logger.critical(
                f"Account locked due to suspicious activity: {email} from {ip_address}"
            )
            return {
                'locked': True,
                'remaining_time': cls.LOCKOUT_DURATION,
                'attempts': attempts
            }

        return {
            'locked': False,
            'attempts': attempts,
            'remaining_attempts': cls.FAILED_LOGIN_THRESHOLD - attempts
        }

    @classmethod
    def record_successful_login(cls, email):
        """
        Record a successful login and clear failed attempts.

        Args:
            email: User's email address
        """
        cache_key = cls.get_cache_key(email)
        cache.delete(cache_key)
        logger.info(f"Successful login for {email}")

    @classmethod
    def is_locked_out(cls, email):
        """
        Check if an email is currently locked out.

        Args:
            email: User's email address

        Returns:
            tuple: (is_locked, remaining_time)
        """
        lockout_key = cls.get_lockout_key(email)
        is_locked = cache.get(lockout_key, False)
        remaining_time = cache.ttl(lockout_key) if is_locked else 0

        return is_locked, remaining_time

    @classmethod
    def get_failed_attempts(cls, email):
        """
        Get number of failed login attempts for an email.

        Args:
            email: User's email address

        Returns:
            int: Number of failed attempts
        """
        cache_key = cls.get_cache_key(email)
        return cache.get(cache_key, 0)

    @classmethod
    def clear_lockout(cls, email):
        """
        Manually clear lockout for an email (admin function).

        Args:
            email: User's email address
        """
        lockout_key = cls.get_lockout_key(email)
        cache_key = cls.get_cache_key(email)
        cache.delete(lockout_key)
        cache.delete(cache_key)
        logger.info(f"Lockout cleared for {email}")
