"""
Utility functions for authentication.

Includes token generation, email verification, and password validation utilities.
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
import logging

logger = logging.getLogger(__name__)


class EmailVerificationTokenGenerator:
    """
    Generate and validate email verification tokens.
    Uses Redis for token storage with expiration.
    """

    TOKEN_EXPIRY = 24 * 60 * 60  # 24 hours in seconds
    TOKEN_LENGTH = 32

    @classmethod
    def generate_token(cls, user):
        """
        Generate a verification token for a user.

        Args:
            user: User instance

        Returns:
            str: Verification token
        """
        # Generate random token
        token = secrets.token_urlsafe(cls.TOKEN_LENGTH)

        # Store token in cache with user ID
        cache_key = f'email_verification_{token}'
        cache.set(cache_key, user.id, cls.TOKEN_EXPIRY)

        logger.info(f"Email verification token generated for user {user.id}")
        return token

    @classmethod
    def verify_token(cls, token):
        """
        Verify a token and return associated user ID.

        Args:
            token: Verification token

        Returns:
            int|None: User ID if valid, None otherwise
        """
        cache_key = f'email_verification_{token}'
        user_id = cache.get(cache_key)

        if user_id:
            # Delete token after successful verification (one-time use)
            cache.delete(cache_key)
            logger.info(f"Email verification token verified for user {user_id}")
            return user_id

        logger.warning(f"Invalid or expired email verification token")
        return None

    @classmethod
    def invalidate_token(cls, token):
        """
        Invalidate a verification token.

        Args:
            token: Verification token
        """
        cache_key = f'email_verification_{token}'
        cache.delete(cache_key)


class PasswordValidator:
    """
    Advanced password strength validator.
    Extends Django's built-in validation with custom rules.
    """

    MIN_LENGTH = 8
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARACTERS = r"[@$!%*?&#^()_+=\-\[\]{}|;:,.<>?/~`]"

    @classmethod
    def validate_password_strength(cls, password, user=None):
        """
        Validate password strength with custom rules.

        Args:
            password: Password to validate
            user: User instance (optional, for context)

        Returns:
            tuple: (is_valid, errors_list)
        """
        errors = []

        # Use Django's built-in validators first
        try:
            validate_password(password, user)
        except ValidationError as e:
            errors.extend(e.messages)

        # Check minimum length
        if len(password) < cls.MIN_LENGTH:
            errors.append(
                f'Le mot de passe doit contenir au moins {cls.MIN_LENGTH} caractères.'
            )

        # Check for uppercase letter
        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            errors.append(
                'Le mot de passe doit contenir au moins une lettre majuscule.'
            )

        # Check for lowercase letter
        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            errors.append(
                'Le mot de passe doit contenir au moins une lettre minuscule.'
            )

        # Check for digit
        if cls.REQUIRE_DIGIT and not re.search(r'\d', password):
            errors.append(
                'Le mot de passe doit contenir au moins un chiffre.'
            )

        # Check for special character
        if cls.REQUIRE_SPECIAL and not re.search(cls.SPECIAL_CHARACTERS, password):
            errors.append(
                'Le mot de passe doit contenir au moins un caractère spécial (@$!%*?&#^()_+=...).'
            )

        # Check for common patterns
        common_patterns = [
            (r'(\w)\1{2,}', 'Le mot de passe ne doit pas contenir de caractères répétés consécutivement.'),
            (r'(012|123|234|345|456|567|678|789|890)', 'Le mot de passe ne doit pas contenir de séquences numériques simples.'),
            (r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',
             'Le mot de passe ne doit pas contenir de séquences alphabétiques simples.'),
        ]

        for pattern, message in common_patterns:
            if re.search(pattern, password.lower()):
                errors.append(message)

        is_valid = len(errors) == 0
        return is_valid, errors

    @classmethod
    def get_password_strength_score(cls, password):
        """
        Calculate password strength score (0-100).

        Args:
            password: Password to score

        Returns:
            int: Strength score
        """
        score = 0

        # Length score (max 30 points)
        length = len(password)
        if length >= 12:
            score += 30
        elif length >= 10:
            score += 20
        elif length >= 8:
            score += 10

        # Character variety (max 40 points)
        if re.search(r'[a-z]', password):
            score += 10
        if re.search(r'[A-Z]', password):
            score += 10
        if re.search(r'\d', password):
            score += 10
        if re.search(cls.SPECIAL_CHARACTERS, password):
            score += 10

        # Additional complexity (max 30 points)
        unique_chars = len(set(password))
        if unique_chars >= 10:
            score += 15
        elif unique_chars >= 8:
            score += 10
        elif unique_chars >= 6:
            score += 5

        # No common patterns
        has_patterns = any(
            re.search(pattern, password.lower())
            for pattern, _ in [
                (r'(\w)\1{2,}', ''),
                (r'(012|123|234|345|456|567|678|789|890)', ''),
                (r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', ''),
            ]
        )
        if not has_patterns:
            score += 15

        return min(score, 100)


class EmailService:
    """
    Service for sending authentication-related emails.
    """

    @classmethod
    def send_verification_email(cls, user, token, request=None):
        """
        Send email verification email.

        Args:
            user: User instance
            token: Verification token
            request: Request object (for building absolute URL)

        Returns:
            bool: True if sent successfully
        """
        try:
            # Build verification URL
            if request:
                base_url = request.build_absolute_uri('/')[:-1]
            else:
                base_url = settings.FRONTEND_URL if hasattr(settings, 'FRONTEND_URL') else 'http://localhost:5173'

            verification_url = f"{base_url}/verify-email/{token}"

            # Prepare email context
            context = {
                'user': user,
                'verification_url': verification_url,
                'expiry_hours': EmailVerificationTokenGenerator.TOKEN_EXPIRY // 3600,
            }

            # Render email template (create template later)
            subject = 'Vérifiez votre adresse email - SPAS'
            html_message = render_to_string('authentication/emails/verify_email.html', context)
            plain_message = strip_tags(html_message)

            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Verification email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
            return False

    @classmethod
    def send_password_reset_email(cls, user, reset_url):
        """
        Send password reset email.

        Args:
            user: User instance
            reset_url: Password reset URL

        Returns:
            bool: True if sent successfully
        """
        try:
            context = {
                'user': user,
                'reset_url': reset_url,
            }

            subject = 'Réinitialisation de mot de passe - SPAS'
            html_message = render_to_string('authentication/emails/password_reset.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Password reset email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
            return False

    @classmethod
    def send_welcome_email(cls, user):
        """
        Send welcome email after successful registration.

        Args:
            user: User instance

        Returns:
            bool: True if sent successfully
        """
        try:
            context = {
                'user': user,
            }

            subject = 'Bienvenue sur SPAS'
            html_message = render_to_string('authentication/emails/welcome.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Welcome email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            return False


def get_client_ip(request):
    """
    Get client IP address from request.

    Args:
        request: Django request object

    Returns:
        str: IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def generate_secure_token(length=32):
    """
    Generate a cryptographically secure random token.

    Args:
        length: Token length

    Returns:
        str: Random token
    """
    return secrets.token_urlsafe(length)
