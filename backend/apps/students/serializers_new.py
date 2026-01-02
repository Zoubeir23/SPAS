"""
Serializers for students app.
"""
from rest_framework import serializers
from .models import Student


class StudentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for student lists."""

    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    full_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'first_name', 'last_name', 'full_name',
            'email', 'status', 'status_display', 'program_name', 'program_code',
            'admission_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_full_name(self, obj):
        """Get student full name."""
        return obj.get_full_name()


class StudentSerializer(serializers.ModelSerializer):
    """Standard serializer for students with nested program info."""

    program_name = serializers.CharField(source='program.name', read_only=True)
    program_code = serializers.CharField(source='program.code', read_only=True)
    full_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'student_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'date_of_birth',
            'program', 'program_name', 'program_code',
            'admission_date', 'expected_graduation_date',
            'status', 'status_display',
            'address', 'emergency_contact_name', 'emergency_contact_phone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        """Get student full name."""
        return obj.get_full_name()


class StudentDetailSerializer(StudentSerializer):
    """Detailed serializer with all relationships and computed fields."""

    total_enrollments = serializers.SerializerMethodField()
    active_enrollments = serializers.SerializerMethodField()
    completed_courses = serializers.SerializerMethodField()
    current_gpa = serializers.SerializerMethodField()
    active_alerts = serializers.SerializerMethodField()
    latest_prediction = serializers.SerializerMethodField()

    class Meta(StudentSerializer.Meta):
        fields = StudentSerializer.Meta.fields + [
            'total_enrollments', 'active_enrollments', 'completed_courses',
            'current_gpa', 'active_alerts', 'latest_prediction'
        ]

    def get_total_enrollments(self, obj):
        return obj.enrollments.count()

    def get_active_enrollments(self, obj):
        return obj.enrollments.filter(status='ENROLLED').count()

    def get_completed_courses(self, obj):
        return obj.enrollments.filter(status='COMPLETED').count()

    def get_current_gpa(self, obj):
        from apps.grades.models import CourseGradeSummary
        completed_enrollments = obj.enrollments.filter(status='COMPLETED')
        summaries = CourseGradeSummary.objects.filter(
            enrollment__in=completed_enrollments,
            gpa_points__isnull=False
        )
        if not summaries.exists():
            return None
        total_gpa = sum(s.gpa_points for s in summaries)
        return round(total_gpa / summaries.count(), 2)

    def get_active_alerts(self, obj):
        return obj.alerts.filter(status='ACTIVE').count()

    def get_latest_prediction(self, obj):
        latest = obj.predictions.filter(is_latest=True).first()
        if latest:
            return {
                'id': latest.id,
                'risk_score': float(latest.risk_score),
                'risk_level': latest.risk_level,
                'is_at_risk': latest.is_at_risk,
                'predicted_at': latest.predicted_at
            }
        return None


class StudentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating students."""

    class Meta:
        model = Student
        fields = [
            'student_id', 'first_name', 'last_name',
            'email', 'phone', 'date_of_birth',
            'program', 'admission_date', 'expected_graduation_date',
            'status', 'address', 'emergency_contact_name', 'emergency_contact_phone'
        ]

    def validate_student_id(self, value):
        if Student.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("A student with this student ID already exists.")
        return value

    def validate_email(self, value):
        if Student.objects.filter(email=value).exists():
            raise serializers.ValidationError("A student with this email already exists.")
        return value
