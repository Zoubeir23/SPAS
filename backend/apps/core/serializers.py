"""
Core serializers for SPAS application.
"""
from rest_framework import serializers
from .models import SystemSettings, AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """Serializer for AuditLog model - used for listing and viewing audit entries."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'action',
            'action_display',
            'model_name',
            'object_id',
            'object_repr',
            'changes',
            'ip_address',
            'endpoint',
            'method',
            'status_code',
            'timestamp',
            'extra_data',
        ]
        read_only_fields = fields
    
    def get_user_name(self, obj) -> str:
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return 'Système'


class AuditLogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing audit logs."""
    
    user_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user_name',
            'action',
            'action_display',
            'model_name',
            'object_repr',
            'timestamp',
            'ip_address',
        ]
    
    def get_user_name(self, obj) -> str:
        if obj.user:
            return obj.user.get_full_name() or obj.user.email
        return 'Système'


class SystemSettingsSerializer(serializers.ModelSerializer):
    """Serializer for SystemSettings model."""
    
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    
    class Meta:
        model = SystemSettings
        fields = [
            # ML Settings
            'ml_auto_training',
            'ml_training_frequency',
            'ml_risk_threshold_low',
            'ml_risk_threshold_medium',
            'ml_risk_threshold_high',
            # Alert Settings
            'alert_auto_create',
            'alert_email_notifications',
            'alert_sms_notifications',
            # Notification Settings
            'notification_email_enabled',
            'notification_sms_enabled',
            'notification_push_enabled',
            # Academic Settings
            'academic_year_start_month',
            'academic_passing_grade',
            'academic_attendance_threshold',
            # System Settings
            'system_language',
            'system_timezone',
            'system_date_format',
            'system_maintenance_mode',
            # Data Retention
            'data_retention_years',
            # Metadata
            'created_at',
            'updated_at',
            'updated_by_name',
        ]
        read_only_fields = ['created_at', 'updated_at', 'updated_by_name']
    
    def validate_ml_risk_threshold_low(self, value):
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Le seuil doit être entre 0 et 1")
        return value
    
    def validate_ml_risk_threshold_medium(self, value):
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Le seuil doit être entre 0 et 1")
        return value
    
    def validate_ml_risk_threshold_high(self, value):
        if not 0 <= value <= 1:
            raise serializers.ValidationError("Le seuil doit être entre 0 et 1")
        return value
    
    def validate_academic_passing_grade(self, value):
        if not 0 <= value <= 20:
            raise serializers.ValidationError("La note doit être entre 0 et 20")
        return value
    
    def validate_academic_attendance_threshold(self, value):
        if not 0 <= value <= 100:
            raise serializers.ValidationError("Le seuil doit être entre 0 et 100")
        return value
