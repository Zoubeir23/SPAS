"""
Serializers for Session app.
"""
from rest_framework import serializers
from .models import Session


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for Session model."""

    student_count = serializers.SerializerMethodField()
    is_current = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            'id', 'name', 'year', 'start_date', 'end_date',
            'status', 'student_count', 'is_current',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_student_count(self, obj):
        """Get number of active students in session."""
        return obj.students.filter(status='active').count()

    def get_is_current(self, obj):
        """Check if session is current."""
        return obj.is_current()


class SessionListSerializer(serializers.ModelSerializer):
    """Minimal serializer for session lists."""

    class Meta:
        model = Session
        fields = ['id', 'name', 'year', 'status']
