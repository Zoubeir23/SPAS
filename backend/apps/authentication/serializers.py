"""
Authentication serializers for JWT-based authentication.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from apps.users.models import User
from .utils import PasswordValidator, EmailVerificationTokenGenerator
from .throttling import SuspiciousActivityDetector


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'role'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'phone': {'required': False},
            'role': {'required': True}
        }

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'Un utilisateur avec cet email existe déjà.'
            )
        return value.lower()

    def validate_password(self, value):
        """Validate password strength using custom validator."""
        is_valid, errors = PasswordValidator.validate_password_strength(value)
        if not is_valid:
            raise serializers.ValidationError(errors)
        return value

    def validate(self, attrs):
        """Validate password confirmation match."""
        if attrs.get('password') != attrs.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': 'Les mots de passe ne correspondent pas.'
            })
        return attrs

    def create(self, validated_data):
        """Create new user."""
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm')

        # Create user with inactive status until email is verified
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', User.Role.TEACHER),
            is_active=False  # Require email verification
        )

        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login with enhanced security."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate and authenticate user with lockout protection."""
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                'Must include "email" and "password".',
                code='authorization'
            )

        # Check if account is locked
        is_locked, remaining_time = SuspiciousActivityDetector.is_locked_out(email)
        if is_locked:
            minutes = remaining_time // 60
            raise serializers.ValidationError(
                f'Compte temporairement verrouillé en raison de tentatives de connexion multiples. '
                f'Réessayez dans {minutes} minutes.',
                code='account_locked'
            )

        # Authenticate user
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                'Impossible de se connecter avec les identifiants fournis.',
                code='authorization'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'Ce compte utilisateur est désactivé. Veuillez vérifier votre email.',
                code='authorization'
            )

        attrs['user'] = user
        return attrs


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""

    token = serializers.CharField(required=True)

    def validate_token(self, value):
        """Validate verification token."""
        user_id = EmailVerificationTokenGenerator.verify_token(value)
        if not user_id:
            raise serializers.ValidationError(
                'Token de vérification invalide ou expiré.'
            )

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Utilisateur introuvable.'
            )

        if user.is_active:
            raise serializers.ValidationError(
                'Cet email a déjà été vérifié.'
            )

        return value

    def save(self):
        """Activate user account."""
        token = self.validated_data['token']
        user_id = EmailVerificationTokenGenerator.verify_token(token)
        user = User.objects.get(pk=user_id)
        user.is_active = True
        user.save()
        return user


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending verification email."""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate email exists."""
        try:
            user = User.objects.get(email__iexact=value)
            if user.is_active:
                raise serializers.ValidationError(
                    'Cet email a déjà été vérifié.'
                )
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist
            pass
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request."""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate that user exists."""
        try:
            User.objects.get(email=value, is_active=True)
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist for security
            pass
        return value

    def save(self):
        """Generate password reset token and send email."""
        email = self.validated_data['email']
        try:
            user = User.objects.get(email=email, is_active=True)

            # Generate token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # In production, send email here
            # For now, return the token (will be logged)
            return {
                'uid': uid,
                'token': token,
                'user': user
            }
        except User.DoesNotExist:
            # Don't reveal that the user doesn't exist
            return None


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation with enhanced validation."""

    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_new_password(self, value):
        """Validate password strength using custom validator."""
        is_valid, errors = PasswordValidator.validate_password_strength(value)
        if not is_valid:
            raise serializers.ValidationError(errors)
        return value

    def validate(self, attrs):
        """Validate token and uid."""
        try:
            uid = force_str(urlsafe_base64_decode(attrs['uid']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError('Lien de réinitialisation invalide.')

        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError('Lien de réinitialisation invalide ou expiré.')

        attrs['user'] = user
        return attrs

    def save(self):
        """Reset user password."""
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password (authenticated users) with enhanced validation."""

    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('L\'ancien mot de passe est incorrect.')
        return value

    def validate_new_password(self, value):
        """Validate new password strength using custom validator."""
        user = self.context['request'].user
        is_valid, errors = PasswordValidator.validate_password_strength(value, user)
        if not is_valid:
            raise serializers.ValidationError(errors)
        return value

    def validate(self, attrs):
        """Ensure new password is different from old password."""
        if attrs.get('old_password') == attrs.get('new_password'):
            raise serializers.ValidationError({
                'new_password': 'Le nouveau mot de passe doit être différent de l\'ancien.'
            })
        return attrs

    def save(self):
        """Change user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordStrengthSerializer(serializers.Serializer):
    """Serializer for checking password strength."""

    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Calculate password strength score and validation."""
        password = attrs['password']
        is_valid, errors = PasswordValidator.validate_password_strength(password)
        score = PasswordValidator.get_password_strength_score(password)

        return {
            'is_valid': is_valid,
            'score': score,
            'errors': errors,
            'strength': self._get_strength_label(score)
        }

    def _get_strength_label(self, score):
        """Get strength label based on score."""
        if score >= 80:
            return 'excellent'
        elif score >= 60:
            return 'good'
        elif score >= 40:
            return 'fair'
        else:
            return 'weak'


class TokenBlacklistStatusSerializer(serializers.Serializer):
    """Serializer for checking if a token is blacklisted."""

    token = serializers.CharField(required=True)

    def validate_token(self, value):
        """Validate token format."""
        if not value:
            raise serializers.ValidationError('Token requis.')
        return value
