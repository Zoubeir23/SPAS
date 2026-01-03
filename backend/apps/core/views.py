"""
Core views for SPAS application.
Contains system-wide views like settings management.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import SystemSettings
from .serializers import SystemSettingsSerializer


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def system_settings(request):
    """
    GET: Retrieve current system settings
    PATCH: Update system settings (admin only)
    """
    settings = SystemSettings.get_settings()
    
    if request.method == 'GET':
        serializer = SystemSettingsSerializer(settings)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        # Only admins can update settings
        if not request.user.is_staff and request.user.role != 'admin':
            return Response(
                {'detail': 'Seuls les administrateurs peuvent modifier les paramètres'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = SystemSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def reset_settings(request):
    """
    POST: Reset all settings to default values
    """
    settings = SystemSettings.get_settings()
    
    # Reset to defaults
    settings.ml_auto_training = True
    settings.ml_training_frequency = 'weekly'
    settings.ml_risk_threshold_low = 0.3
    settings.ml_risk_threshold_medium = 0.6
    settings.ml_risk_threshold_high = 0.8
    settings.alert_auto_create = True
    settings.alert_email_notifications = True
    settings.alert_sms_notifications = False
    settings.notification_email_enabled = True
    settings.notification_sms_enabled = False
    settings.notification_push_enabled = True
    settings.academic_year_start_month = 9
    settings.academic_passing_grade = 10.0
    settings.academic_attendance_threshold = 75.0
    settings.system_language = 'fr'
    settings.system_timezone = 'Africa/Dakar'
    settings.system_date_format = 'DD/MM/YYYY'
    settings.system_maintenance_mode = False
    settings.data_retention_years = 7
    settings.updated_by = request.user
    settings.save()
    
    serializer = SystemSettingsSerializer(settings)
    return Response({
        'message': 'Paramètres réinitialisés avec succès',
        'data': serializer.data
    })
