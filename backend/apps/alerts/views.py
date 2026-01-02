"""
Views for Alert app.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Alert, Intervention
from .serializers import (
    AlertSerializer, AlertListSerializer,
    InterventionSerializer, InterventionListSerializer, InterventionCreateSerializer
)


class AlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Alert model.

    Provides CRUD operations and custom actions:
    - GET /alerts/ - List all alerts
    - POST /alerts/ - Create an alert
    - GET /alerts/{id}/ - Retrieve an alert
    - PUT/PATCH /alerts/{id}/ - Update an alert
    - DELETE /alerts/{id}/ - Delete an alert
    - POST /alerts/{id}/acknowledge/ - Acknowledge an alert
    - POST /alerts/{id}/resolve/ - Resolve an alert
    - GET /alerts/active/ - Get all active alerts
    - GET /alerts/statistics/ - Get alert statistics
    """
    queryset = Alert.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'type', 'level', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'student__matricule', 'message']
    ordering_fields = ['level', 'status', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return AlertListSerializer
        return AlertSerializer

    def get_queryset(self):
        """Optimize queryset with select_related."""
        queryset = Alert.objects.select_related('student', 'student__program')

        # Filter by type
        alert_type = self.request.query_params.get('type', None)
        if alert_type:
            queryset = queryset.filter(type=alert_type)

        # Filter by level
        level = self.request.query_params.get('level', None)
        if level:
            queryset = queryset.filter(level=level)

        # Filter by status
        alert_status = self.request.query_params.get('status', None)
        if alert_status:
            queryset = queryset.filter(status=alert_status)

        return queryset

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """
        Acknowledge an alert.

        POST /alerts/{id}/acknowledge/
        """
        alert = self.get_object()

        if alert.status != Alert.Status.NEW:
            return Response(
                {'error': 'Seules les nouvelles alertes peuvent être accusées réception.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        alert.acknowledge()

        return Response({
            'success': True,
            'message': 'Alerte accusée réception.',
            'data': AlertSerializer(alert).data
        })

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Resolve an alert.

        POST /alerts/{id}/resolve/
        """
        alert = self.get_object()

        if alert.status == Alert.Status.RESOLVED:
            return Response(
                {'error': 'Cette alerte est déjà résolue.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        alert.resolve()

        return Response({
            'success': True,
            'message': 'Alerte résolue.',
            'data': AlertSerializer(alert).data
        })

    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active (non-resolved) alerts.

        GET /alerts/active/
        """
        active_alerts = self.get_queryset().filter(
            status__in=[Alert.Status.NEW, Alert.Status.ACKNOWLEDGED]
        ).order_by('-level', '-created_at')

        serializer = self.get_serializer(active_alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def critical(self, request):
        """
        Get all critical-level alerts.

        GET /alerts/critical/
        """
        critical_alerts = self.get_queryset().filter(
            level=Alert.Level.CRITICAL,
            status__in=[Alert.Status.NEW, Alert.Status.ACKNOWLEDGED]
        ).order_by('-created_at')

        serializer = self.get_serializer(critical_alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get alert statistics.

        GET /alerts/statistics/
        """
        queryset = self.get_queryset()

        stats = {
            'total_alerts': queryset.count(),
            'new_alerts': queryset.filter(status=Alert.Status.NEW).count(),
            'acknowledged_alerts': queryset.filter(status=Alert.Status.ACKNOWLEDGED).count(),
            'resolved_alerts': queryset.filter(status=Alert.Status.RESOLVED).count(),
        }

        # Level distribution
        level_distribution = {
            'low': queryset.filter(level=Alert.Level.LOW).count(),
            'medium': queryset.filter(level=Alert.Level.MEDIUM).count(),
            'high': queryset.filter(level=Alert.Level.HIGH).count(),
            'critical': queryset.filter(level=Alert.Level.CRITICAL).count(),
        }

        # Type distribution
        type_distribution = {
            'performance': queryset.filter(type=Alert.AlertType.PERFORMANCE).count(),
            'attendance': queryset.filter(type=Alert.AlertType.ATTENDANCE).count(),
            'risk': queryset.filter(type=Alert.AlertType.RISK).count(),
            'prediction': queryset.filter(type=Alert.AlertType.PREDICTION).count(),
        }

        return Response({
            'statistics': stats,
            'level_distribution': level_distribution,
            'type_distribution': type_distribution
        })

    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)')
    def student_alerts(self, request, student_id=None):
        """
        Get all alerts for a specific student.

        GET /alerts/student/{student_id}/
        """
        alerts = self.get_queryset().filter(
            student_id=student_id
        ).order_by('-created_at')

        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)


class InterventionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Intervention model.

    Provides CRUD operations and custom actions:
    - GET /interventions/ - List all interventions
    - POST /interventions/ - Create an intervention
    - GET /interventions/{id}/ - Retrieve an intervention
    - PUT/PATCH /interventions/{id}/ - Update an intervention
    - DELETE /interventions/{id}/ - Delete an intervention
    - POST /interventions/{id}/complete/ - Mark as completed
    - POST /interventions/{id}/cancel/ - Cancel an intervention
    - GET /interventions/student/{student_id}/ - Get interventions for a student
    """
    queryset = Intervention.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['student', 'type', 'priority', 'status', 'responsible']
    search_fields = ['student__first_name', 'student__last_name', 'student__matricule', 'description']
    ordering_fields = ['scheduled_date', 'priority', 'status', 'created_at']
    ordering = ['-scheduled_date']

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return InterventionListSerializer
        if self.action == 'create':
            return InterventionCreateSerializer
        return InterventionSerializer

    def get_queryset(self):
        """Optimize queryset with select_related."""
        return Intervention.objects.select_related(
            'student', 'student__program', 'responsible', 'alert'
        )

    def perform_create(self, serializer):
        """Auto-assign current user as responsible if not specified."""
        if not serializer.validated_data.get('responsible'):
            serializer.save(responsible=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Mark intervention as completed.

        POST /interventions/{id}/complete/
        """
        intervention = self.get_object()
        outcome = request.data.get('outcome', '')
        
        if intervention.status == Intervention.Status.COMPLETED:
            return Response(
                {'error': 'Cette intervention est déjà terminée.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        intervention.complete(outcome=outcome)

        return Response({
            'success': True,
            'message': 'Intervention terminée avec succès.',
            'data': InterventionSerializer(intervention).data
        })

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an intervention.

        POST /interventions/{id}/cancel/
        """
        intervention = self.get_object()
        
        if intervention.status in [Intervention.Status.COMPLETED, Intervention.Status.CANCELLED]:
            return Response(
                {'error': 'Cette intervention ne peut plus être annulée.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        intervention.cancel()

        return Response({
            'success': True,
            'message': 'Intervention annulée.',
            'data': InterventionSerializer(intervention).data
        })

    @action(detail=False, methods=['get'], url_path='student/(?P<student_id>[^/.]+)')
    def student_interventions(self, request, student_id=None):
        """
        Get all interventions for a specific student.

        GET /interventions/student/{student_id}/
        """
        interventions = self.get_queryset().filter(
            student_id=student_id
        ).order_by('-scheduled_date')

        serializer = self.get_serializer(interventions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending interventions for the current user.

        GET /interventions/pending/
        """
        pending = self.get_queryset().filter(
            responsible=request.user,
            status__in=[Intervention.Status.PLANNED, Intervention.Status.IN_PROGRESS]
        ).order_by('scheduled_date')

        serializer = self.get_serializer(pending, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get intervention statistics.

        GET /interventions/statistics/
        """
        queryset = self.get_queryset()

        stats = {
            'total': queryset.count(),
            'planned': queryset.filter(status=Intervention.Status.PLANNED).count(),
            'in_progress': queryset.filter(status=Intervention.Status.IN_PROGRESS).count(),
            'completed': queryset.filter(status=Intervention.Status.COMPLETED).count(),
            'cancelled': queryset.filter(status=Intervention.Status.CANCELLED).count(),
        }

        # Type distribution
        type_distribution = {}
        for choice in Intervention.InterventionType.choices:
            type_distribution[choice[0]] = queryset.filter(type=choice[0]).count()

        return Response({
            'statistics': stats,
            'type_distribution': type_distribution
        })
