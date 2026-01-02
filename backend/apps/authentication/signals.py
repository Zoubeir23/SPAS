"""
Authentication signals for tracking user events.

Implements logging and notifications for authentication-related events.
"""
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver, Signal
from django.utils import timezone
from django.core.cache import cache
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)

# Custom signals
email_verified = Signal()
password_changed = Signal()
password_reset_requested = Signal()
password_reset_completed = Signal()
suspicious_activity_detected = Signal()


class AuthenticationEvent:
    """
    Authentication event types for logging.
    """
    LOGIN_SUCCESS = 'login_success'
    LOGIN_FAILED = 'login_failed'
    LOGOUT = 'logout'
    PASSWORD_CHANGED = 'password_changed'
    PASSWORD_RESET_REQUESTED = 'password_reset_requested'
    PASSWORD_RESET_COMPLETED = 'password_reset_completed'
    EMAIL_VERIFIED = 'email_verified'
    REGISTRATION = 'registration'
    ACCOUNT_LOCKED = 'account_locked'
    SUSPICIOUS_ACTIVITY = 'suspicious_activity'


def log_authentication_event(user, event_type, ip_address=None, user_agent=None, extra_data=None):
    """
    Log an authentication event.

    Args:
        user: User instance or email
        event_type: Type of event (from AuthenticationEvent)
        ip_address: IP address of the request
        user_agent: User agent string
        extra_data: Additional data to log
    """
    user_identifier = user.email if hasattr(user, 'email') else user

    log_data = {
        'event': event_type,
        'user': user_identifier,
        'timestamp': timezone.now().isoformat(),
        'ip_address': ip_address,
        'user_agent': user_agent,
    }

    if extra_data:
        log_data.update(extra_data)

    # Log to Django logger
    if event_type in [
        AuthenticationEvent.LOGIN_FAILED,
        AuthenticationEvent.ACCOUNT_LOCKED,
        AuthenticationEvent.SUSPICIOUS_ACTIVITY
    ]:
        logger.warning(f"Auth Event: {log_data}")
    elif event_type == AuthenticationEvent.LOGIN_SUCCESS:
        logger.info(f"Auth Event: {log_data}")
    else:
        logger.debug(f"Auth Event: {log_data}")

    # Store event in cache for recent activity tracking
    cache_key = f'auth_events_{user_identifier}'
    recent_events = cache.get(cache_key, [])
    recent_events.append(log_data)

    # Keep only last 10 events
    recent_events = recent_events[-10:]
    cache.set(cache_key, recent_events, 86400)  # 24 hours


@receiver(user_logged_in)
def on_user_logged_in(sender, request, user, **kwargs):
    """
    Signal handler for successful login.
    """
    ip_address = get_ip_from_request(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    log_authentication_event(
        user=user,
        event_type=AuthenticationEvent.LOGIN_SUCCESS,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data={'method': 'jwt'}
    )

    # Update last login timestamp (already handled by Django, but we can add custom logic)
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    logger.info(f"User logged in: {user.email} from {ip_address}")


@receiver(user_logged_out)
def on_user_logged_out(sender, request, user, **kwargs):
    """
    Signal handler for logout.
    """
    if user:
        ip_address = get_ip_from_request(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        log_authentication_event(
            user=user,
            event_type=AuthenticationEvent.LOGOUT,
            ip_address=ip_address,
            user_agent=user_agent
        )

        logger.info(f"User logged out: {user.email}")


@receiver(user_login_failed)
def on_user_login_failed(sender, credentials, request, **kwargs):
    """
    Signal handler for failed login attempts.
    """
    email = credentials.get('username', 'unknown')
    ip_address = get_ip_from_request(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    log_authentication_event(
        user=email,
        event_type=AuthenticationEvent.LOGIN_FAILED,
        ip_address=ip_address,
        user_agent=user_agent
    )

    logger.warning(f"Failed login attempt for: {email} from {ip_address}")


@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    """
    Signal handler for new user registration.
    """
    if created:
        log_authentication_event(
            user=instance,
            event_type=AuthenticationEvent.REGISTRATION,
            extra_data={
                'role': instance.role,
                'is_active': instance.is_active
            }
        )

        logger.info(f"New user registered: {instance.email} with role {instance.role}")


@receiver(email_verified)
def on_email_verified(sender, user, **kwargs):
    """
    Signal handler for email verification.
    """
    log_authentication_event(
        user=user,
        event_type=AuthenticationEvent.EMAIL_VERIFIED
    )

    logger.info(f"Email verified for user: {user.email}")


@receiver(password_changed)
def on_password_changed(sender, user, request=None, **kwargs):
    """
    Signal handler for password changes.
    """
    ip_address = get_ip_from_request(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None

    log_authentication_event(
        user=user,
        event_type=AuthenticationEvent.PASSWORD_CHANGED,
        ip_address=ip_address,
        user_agent=user_agent
    )

    logger.info(f"Password changed for user: {user.email}")


@receiver(password_reset_requested)
def on_password_reset_requested(sender, user, request=None, **kwargs):
    """
    Signal handler for password reset requests.
    """
    ip_address = get_ip_from_request(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None

    log_authentication_event(
        user=user,
        event_type=AuthenticationEvent.PASSWORD_RESET_REQUESTED,
        ip_address=ip_address,
        user_agent=user_agent
    )

    logger.info(f"Password reset requested for user: {user.email}")


@receiver(password_reset_completed)
def on_password_reset_completed(sender, user, request=None, **kwargs):
    """
    Signal handler for completed password resets.
    """
    ip_address = get_ip_from_request(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None

    log_authentication_event(
        user=user,
        event_type=AuthenticationEvent.PASSWORD_RESET_COMPLETED,
        ip_address=ip_address,
        user_agent=user_agent
    )

    logger.info(f"Password reset completed for user: {user.email}")


@receiver(suspicious_activity_detected)
def on_suspicious_activity(sender, user, activity_type, request=None, **kwargs):
    """
    Signal handler for suspicious activities.
    """
    ip_address = get_ip_from_request(request) if request else None
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else None

    log_authentication_event(
        user=user,
        event_type=AuthenticationEvent.SUSPICIOUS_ACTIVITY,
        ip_address=ip_address,
        user_agent=user_agent,
        extra_data={'activity_type': activity_type}
    )

    logger.warning(
        f"Suspicious activity detected for user: {user} - Type: {activity_type}"
    )


def get_ip_from_request(request):
    """
    Extract IP address from request.

    Args:
        request: Django request object

    Returns:
        str: IP address
    """
    if not request:
        return None

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_recent_auth_events(user_email, limit=10):
    """
    Get recent authentication events for a user.

    Args:
        user_email: User's email address
        limit: Maximum number of events to return

    Returns:
        list: Recent authentication events
    """
    cache_key = f'auth_events_{user_email}'
    events = cache.get(cache_key, [])
    return events[-limit:]
