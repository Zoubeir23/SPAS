"""
Serializers for User app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    full_name = serializers.CharField(source='get_full_name', read_only=True)

    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'avatar', 'avatar_url', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_avatar_url(self, obj):
        """Return the full URL of the avatar."""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating users."""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        error_messages={
            'required': 'Le mot de passe est requis.',
            'min_length': 'Le mot de passe doit contenir au moins 8 caractères.'
        }
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            'required': 'La confirmation du mot de passe est requise.'
        }
    )

    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone'
        ]
        extra_kwargs = {
            'email': {
                'error_messages': {
                    'required': 'L\'email est requis.',
                    'invalid': 'Veuillez entrer une adresse email valide.',
                    'unique': 'Un utilisateur avec cet email existe déjà.'
                }
            },
            'first_name': {
                'error_messages': {
                    'required': 'Le prénom est requis.',
                    'max_length': 'Le prénom ne peut pas dépasser 100 caractères.'
                }
            },
            'last_name': {
                'error_messages': {
                    'required': 'Le nom est requis.',
                    'max_length': 'Le nom ne peut pas dépasser 100 caractères.'
                }
            },
            'role': {
                'error_messages': {
                    'required': 'Le rôle est requis.',
                    'invalid_choice': 'Le rôle sélectionné n\'est pas valide.'
                }
            }
        }

    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if not value or not value.strip():
            raise serializers.ValidationError("L'email ne peut pas être vide.")
        value = value.strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà.")
        return value

    def validate_first_name(self, value):
        """Validate first name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Le prénom ne peut pas être vide.")
        return value.strip()

    def validate_last_name(self, value):
        """Validate last name."""
        if not value or not value.strip():
            raise serializers.ValidationError("Le nom ne peut pas être vide.")
        return value.strip()

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Les mots de passe ne correspondent pas."
            })
        return attrs

    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users."""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'avatar', 'is_active'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Validate passwords."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Les nouveaux mots de passe ne correspondent pas."
            })
        return attrs

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("L'ancien mot de passe est incorrect.")
        return value

    def save(self, **kwargs):
        """Update user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
