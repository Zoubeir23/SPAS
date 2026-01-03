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
