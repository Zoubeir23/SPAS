"""
Core views for SPAS application.
Contains system-wide views like settings management and audit logs.
"""

from rest_framework import status, viewsets, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import SystemSettings, AuditLog
from .permissions import IsAdmin
from .serializers import (
    SystemSettingsSerializer,
    AuditLogSerializer,
    AuditLogListSerializer,
)


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour consulter les logs d'audit.

    Accessible uniquement aux administrateurs.
    Lecture seule - les logs ne peuvent pas être modifiés ou supprimés via l'API.

    Actions disponibles:
    - list: Liste tous les logs avec pagination et filtres
    - retrieve: Détails d'un log spécifique
    - statistics: Statistiques sur les actions
    - recent: Les 10 dernières actions
    """

    queryset = AuditLog.objects.select_related("user").order_by("-timestamp")
    permission_classes = [IsAuthenticated, IsAdmin]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["action", "model_name", "user"]
    search_fields = ["object_repr", "ip_address", "endpoint", "user__email"]
    ordering_fields = ["timestamp", "action", "model_name"]
    ordering = ["-timestamp"]

    def get_serializer_class(self):
        if self.action == "list":
            return AuditLogListSerializer
        return AuditLogSerializer

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Retourne des statistiques sur les logs d'audit."""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta

        # Stats des 30 derniers jours
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_logs = self.queryset.filter(timestamp__gte=thirty_days_ago)

        # Actions par type
        actions_count = (
            recent_logs.values("action").annotate(count=Count("id")).order_by("-count")
        )

        # Actions par modèle
        models_count = (
            recent_logs.values("model_name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        # Utilisateurs les plus actifs
        active_users = (
            recent_logs.exclude(user__isnull=True)
            .values("user__email")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )

        return Response(
            {
                "total_logs": self.queryset.count(),
                "logs_last_30_days": recent_logs.count(),
                "actions_by_type": list(actions_count),
                "actions_by_model": list(models_count),
                "most_active_users": list(active_users),
            }
        )

    @action(detail=False, methods=["get"])
    def recent(self, request):
        """Retourne les 10 dernières actions."""
        recent = self.queryset[:10]
        serializer = AuditLogListSerializer(recent, many=True)
        return Response(serializer.data)


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def system_settings(request):
    """
    GET: Retrieve current system settings
    PATCH: Update system settings (admin only)
    """
    settings = SystemSettings.get_settings()

    if request.method == "GET":
        serializer = SystemSettingsSerializer(settings)
        return Response(serializer.data)

    elif request.method == "PATCH":
        # Only admins can update settings (strict role check, not is_staff)
        if request.user.role != "admin":
            return Response(
                {"detail": "Seuls les administrateurs peuvent modifier les paramètres"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SystemSettingsSerializer(settings, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdmin])
def reset_settings(request):
    """
    POST: Reset all settings to default values
    """
    settings = SystemSettings.get_settings()

    # Reset to defaults
    settings.ml_auto_training = True
    settings.ml_training_frequency = "weekly"
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
    settings.system_language = "fr"
    settings.system_timezone = "Africa/Dakar"
    settings.system_date_format = "DD/MM/YYYY"
    settings.system_maintenance_mode = False
    settings.data_retention_years = 7
    settings.updated_by = request.user
    settings.save()

    serializer = SystemSettingsSerializer(settings)
    return Response(
        {"message": "Paramètres réinitialisés avec succès", "data": serializer.data}
    )
