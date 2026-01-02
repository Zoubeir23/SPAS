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

    class Meta:
        model = Student
        fields = [
            'id', 'matricule', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'date_of_birth', 'program', 'program_name',
            'session', 'session_name', 'status',
            'risk_score', 'risk_level',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating students."""

    class Meta:
        model = Student
        fields = [
            'matricule', 'first_name', 'last_name', 'email', 'phone',
            'date_of_birth', 'program', 'session', 'status'
        ]


class StudentListSerializer(serializers.ModelSerializer):
    """Minimal serializer for student lists."""

    full_name = serializers.CharField(source='get_full_name', read_only=True)
    program_name = serializers.CharField(source='program.name', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'matricule', 'full_name', 'email',
            'program_name', 'status', 'risk_score', 'risk_level'
        ]
