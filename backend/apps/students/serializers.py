"""
Serializers for Student app.
"""
from rest_framework import serializers
from .models import Student


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for Student model."""

    full_name = serializers.CharField(source='get_full_name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)

    level_display = serializers.CharField(source='get_level_display', read_only=True)

    photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'matricule', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'date_of_birth', 'photo', 'photo_url',
            'program', 'program_name', 'session', 'session_name', 
            'status', 'level', 'level_display', 'risk_score', 'risk_level',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_photo_url(self, obj):
        """Return the full URL of the photo."""
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating students."""

    class Meta:
        model = Student
        fields = [
            'matricule', 'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'photo', 'program', 'session', 'status', 'level'
        ]
        extra_kwargs = {
            'matricule': {
                'error_messages': {
                    'required': 'Le matricule est requis.',
                    'unique': 'Un étudiant avec ce matricule existe déjà.',
                    'max_length': 'Le matricule ne peut pas dépasser 50 caractères.'
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
            'email': {
                'error_messages': {
                    'required': 'L\'email est requis.',
                    'invalid': 'Veuillez entrer une adresse email valide.',
                    'unique': 'Un étudiant avec cet email existe déjà.'
                }
            },
            'date_of_birth': {
                'error_messages': {
                    'required': 'La date de naissance est requise.',
                    'invalid': 'Veuillez entrer une date valide.'
                }
            },
            'program': {
                'error_messages': {
                    'required': 'La filière est requise.',
                    'does_not_exist': 'La filière sélectionnée n\'existe pas.'
                }
            },
            'session': {
                'error_messages': {
                    'required': 'La session est requise.',
                    'does_not_exist': 'La session sélectionnée n\'existe pas.'
                }
            },
            'level': {
                'error_messages': {
                    'required': 'Le niveau est requis.',
                    'invalid_choice': 'Le niveau sélectionné n\'est pas valide.'
                }
            }
        }

    def validate_matricule(self, value):
        """Validate matricule format."""
        if not value or not value.strip():
            raise serializers.ValidationError("Le matricule ne peut pas être vide.")
        return value.strip().upper()

    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if not value or not value.strip():
            raise serializers.ValidationError("L'email ne peut pas être vide.")
        value = value.strip().lower()
        if Student.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Un étudiant avec cet email existe déjà.")
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


class StudentListSerializer(serializers.ModelSerializer):
    """Minimal serializer for student lists."""

    full_name = serializers.CharField(source='get_full_name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'matricule', 'full_name', 'email',
            'program_name', 'status', 'level', 'risk_score', 'risk_level'
        ]
