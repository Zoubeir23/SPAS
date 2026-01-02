"""
Serializers for Attendance app.
"""
from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    """Serializer for Attendance model."""

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_matricule = serializers.CharField(source='student.matricule', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'student_name', 'student_matricule',
            'subject', 'subject_name', 'subject_code',
            'date', 'status', 'justification',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AttendanceListSerializer(serializers.ModelSerializer):
    """Minimal serializer for attendance lists."""

    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'student_name', 'subject_code', 'date', 'status']


class AttendanceCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating attendance records."""

    class Meta:
        model = Attendance
        fields = ['student', 'subject', 'date', 'status', 'justification']
