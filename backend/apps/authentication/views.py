"""
Authentication views for JWT-based authentication with enhanced security.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer,
    PasswordStrengthSerializer,
    TokenBlacklistStatusSerializer
)
from .throttling import (
    LoginRateThrottle,
    RegisterRateThrottle,
    PasswordResetRateThrottle,
    EmailVerificationRateThrottle,
    TokenRefreshRateThrottle
)
from .utils import EmailVerificationTokenGenerator, EmailService, get_client_ip
from .signals import (
    email_verified,
    password_changed,
    password_reset_requested,
    password_reset_completed
)
from apps.users.serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)


@extend_schema(
    tags=['Authentication'],
    request=RegisterSerializer,
    responses={
        201: OpenApiResponse(
            description='User registered successfully',
            response={
                'type': 'object',
                'properties': {
                    'message': {'type': 'string'},
                    'user': {'type': 'object'},
                    'verification_token': {'type': 'string'}
                }
            }
        ),
        400: OpenApiResponse(description='Validation error'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([RegisterRateThrottle])
def register_view(request):
    """
    Register a new user account.

    Creates a new user with inactive status and sends email verification.
    """
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    # Generate email verification token
    verification_token = EmailVerificationTokenGenerator.generate_token(user)

    # Send verification email
    EmailService.send_verification_email(user, verification_token, request)

    logger.info(f"New user registered: {user.email}")

    return Response({
        'message': 'Utilisateur créé avec succès. Veuillez vérifier votre email.',
        'user': UserSerializer(user).data,
        'verification_token': verification_token  # Remove in production, only for dev/testing
    }, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Authentication'],
    request=EmailVerificationSerializer,
    responses={
        200: OpenApiResponse(description='Email verified successfully'),
        400: OpenApiResponse(description='Invalid or expired token'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_view(request):
    """
    Verify user email with token.

    Activates user account after successful verification.
    """
    serializer = EmailVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    # Send signal
    email_verified.send(sender=verify_email_view, user=user)

    # Send welcome email
    EmailService.send_welcome_email(user)

    logger.info(f"Email verified for user: {user.email}")

    return Response({
        'message': 'Email vérifié avec succès. Vous pouvez maintenant vous connecter.'
    }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    request=ResendVerificationSerializer,
    responses={
        200: OpenApiResponse(description='Verification email sent'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([EmailVerificationRateThrottle])
def resend_verification_view(request):
    """
    Resend email verification link.

    Generates new verification token and sends email.
    Always returns success to prevent email enumeration.
    """
    serializer = ResendVerificationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email = serializer.validated_data['email']

    try:
        from apps.users.models import User
        user = User.objects.get(email__iexact=email, is_active=False)

        # Generate new token
        verification_token = EmailVerificationTokenGenerator.generate_token(user)

        # Send email
        EmailService.send_verification_email(user, verification_token, request)

        logger.info(f"Verification email resent to: {email}")
    except User.DoesNotExist:
        # Don't reveal that user doesn't exist
        pass

    return Response({
        'message': 'Si votre email existe et n\'est pas encore vérifié, '
                   'vous recevrez un email de vérification.'
    }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(
            description='Login successful',
            response={
                'type': 'object',
                'properties': {
                    'access': {'type': 'string'},
                    'refresh': {'type': 'string'},
                    'user': {'type': 'object'}
                }
            }
        ),
        400: OpenApiResponse(description='Invalid credentials or account locked'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_view(request):
    """
    Authenticate user and return JWT tokens.

    Returns access token, refresh token, and user data.
    Implements account lockout protection against brute force attacks.
    """
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data['user']

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)

    # Serialize user data
    user_serializer = UserSerializer(user)

    logger.info(f"User logged in: {user.email} from {get_client_ip(request)}")

    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': user_serializer.data
    }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    request={
        'type': 'object',
        'properties': {
            'refresh': {'type': 'string'}
        }
    },
    responses={
        200: OpenApiResponse(description='Logout successful'),
        400: OpenApiResponse(description='Invalid token'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user by blacklisting the refresh token.

    Requires refresh token in request body.
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'detail': 'Le token de rafraîchissement est requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token = RefreshToken(refresh_token)
        token.blacklist()

        logger.info(f"User logged out: {request.user.email}")

        return Response(
            {'detail': 'Déconnexion réussie.'},
            status=status.HTTP_200_OK
        )
    except TokenError:
        return Response(
            {'detail': 'Token invalide ou expiré.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    tags=['Authentication'],
    request=PasswordResetRequestSerializer,
    responses={
        200: OpenApiResponse(description='Password reset email sent'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetRateThrottle])
def password_reset_request_view(request):
    """
    Request password reset.

    Sends password reset email to user if email exists.
    Always returns 200 for security (doesn't reveal if email exists).
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Send reset email
    reset_data = serializer.save()

    # Send signal and log
    if reset_data:
        user = reset_data['user']
        password_reset_requested.send(
            sender=password_reset_request_view,
            user=user,
            request=request
        )

        # Build reset URL
        base_url = request.build_absolute_uri('/')[:-1]
        reset_url = f"{base_url}/reset-password/{reset_data['uid']}/{reset_data['token']}/"

        # Send email
        EmailService.send_password_reset_email(user, reset_url)

        logger.info(f"Password reset requested for {user.email}")

    # Always return success to prevent email enumeration
    return Response(
        {
            'detail': 'Si votre email existe dans notre système, vous recevrez '
                     'les instructions de réinitialisation de mot de passe.'
        },
        status=status.HTTP_200_OK
    )


@extend_schema(
    tags=['Authentication'],
    request=PasswordResetConfirmSerializer,
    responses={
        200: OpenApiResponse(description='Password reset successful'),
        400: OpenApiResponse(description='Invalid or expired token'),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    """
    Confirm password reset with token.

    Resets user password using the provided token and new password.
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.save()

    # Send signal
    password_reset_completed.send(
        sender=password_reset_confirm_view,
        user=user,
        request=request
    )

    logger.info(f"Password reset completed for {user.email}")

    return Response(
        {'detail': 'Le mot de passe a été réinitialisé avec succès.'},
        status=status.HTTP_200_OK
    )


@extend_schema(
    tags=['Authentication'],
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(description='Password changed successfully'),
        400: OpenApiResponse(description='Invalid old password'),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Change password for authenticated user.

    Requires old password for verification.
    """
    serializer = ChangePasswordSerializer(
        data=request.data,
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)

    serializer.save()

    # Send signal
    password_changed.send(
        sender=change_password_view,
        user=request.user,
        request=request
    )

    logger.info(f"Password changed for user: {request.user.email}")

    return Response(
        {'detail': 'Le mot de passe a été changé avec succès.'},
        status=status.HTTP_200_OK
    )


@extend_schema(
    tags=['Authentication'],
    request=PasswordStrengthSerializer,
    responses={
        200: OpenApiResponse(
            description='Password strength check',
            response={
                'type': 'object',
                'properties': {
                    'is_valid': {'type': 'boolean'},
                    'score': {'type': 'integer'},
                    'strength': {'type': 'string'},
                    'errors': {'type': 'array', 'items': {'type': 'string'}}
                }
            }
        ),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_password_strength_view(request):
    """
    Check password strength without saving.

    Returns strength score (0-100) and validation errors.
    """
    serializer = PasswordStrengthSerializer(data=request.data)
    result = serializer.validate(request.data)

    return Response(result, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    responses={
        200: OpenApiResponse(
            description='Current user data',
            response=UserSerializer
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Get current authenticated user data.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    tags=['Authentication'],
    request=TokenBlacklistStatusSerializer,
    responses={
        200: OpenApiResponse(
            description='Token blacklist status',
            response={
                'type': 'object',
                'properties': {
                    'is_blacklisted': {'type': 'boolean'}
                }
            }
        ),
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def check_token_blacklist_view(request):
    """
    Check if a refresh token is blacklisted.

    Useful for client-side token validation.
    """
    serializer = TokenBlacklistStatusSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    token_value = serializer.validated_data['token']

    try:
        # Try to create RefreshToken instance
        token = RefreshToken(token_value)

        # Check if token is blacklisted
        jti = token.payload.get('jti')
        is_blacklisted = BlacklistedToken.objects.filter(
            token__jti=jti
        ).exists()

        return Response({
            'is_blacklisted': is_blacklisted
        }, status=status.HTTP_200_OK)

    except TokenError:
        return Response({
            'detail': 'Token invalide.'
        }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=['Authentication'],
    responses={
        200: OpenApiResponse(
            description='List of recent authentication events',
            response={
                'type': 'object',
                'properties': {
                    'events': {'type': 'array', 'items': {'type': 'object'}}
                }
            }
        ),
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_activity_view(request):
    """
    Get recent authentication activity for current user.

    Returns list of recent login attempts and security events.
    """
    from .signals import get_recent_auth_events

    events = get_recent_auth_events(request.user.email)

    return Response({
        'events': events
    }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Authentication'],
    responses={
        200: OpenApiResponse(
            description='All tokens blacklisted successfully'
        ),
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_all_devices_view(request):
    """
    Logout from all devices by blacklisting all outstanding tokens.

    Useful for security if user suspects account compromise.
    """
    try:
        # Get all outstanding tokens for this user
        tokens = OutstandingToken.objects.filter(user=request.user)

        # Blacklist each token
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        logger.info(f"All devices logged out for user: {request.user.email}")

        return Response({
            'detail': f'{tokens.count()} appareils déconnectés avec succès.'
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error logging out all devices: {str(e)}")
        return Response({
            'detail': 'Erreur lors de la déconnexion de tous les appareils.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
