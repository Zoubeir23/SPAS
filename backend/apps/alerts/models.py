"""
Alert models for SPAS.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Alert(models.Model):
    """Alert model - Represents automated alerts for student issues."""

    class AlertType(models.TextChoices):
        """Alert type choices."""
        PERFORMANCE = 'performance', _('Performance')
        ATTENDANCE = 'attendance', _('Présence')
        RISK = 'risk', _('Risque')
        PREDICTION = 'prediction', _('Prédiction')

    class Level(models.TextChoices):
        """Alert level choices."""
        LOW = 'low', _('Faible')
        MEDIUM = 'medium', _('Moyen')
        HIGH = 'high', _('Élevé')
        CRITICAL = 'critical', _('Critique')

    class Status(models.TextChoices):
        """Alert status choices."""
        NEW = 'new', _('Nouveau')
        ACKNOWLEDGED = 'acknowledged', _('Accusé réception')
        RESOLVED = 'resolved', _('Résolu')

    # Alert Information
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='alerts',
        verbose_name=_('student')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=AlertType.choices,
        db_index=True
    )
    level = models.CharField(
        _('level'),
        max_length=20,
        choices=Level.choices,
        db_index=True
    )
    message = models.TextField(_('message'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
        db_index=True
    )

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)
    acknowledged_at = models.DateTimeField(_('acknowledged at'), null=True, blank=True)
    resolved_at = models.DateTimeField(_('resolved at'), null=True, blank=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'alerts'
        verbose_name = _('alert')
        verbose_name_plural = _('alerts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['type', 'level']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.student.get_full_name()} - {self.level}"

    @property
    def student_name(self):
        """Return the student's full name."""
        return self.student.get_full_name() if self.student else None

    @property
    def program_name(self):
        """Return the student's program name."""
        return self.student.program.name if self.student and self.student.program else None

    def acknowledge(self):
        """Mark alert as acknowledged."""
        from django.utils import timezone
        if self.status == self.Status.NEW:
            self.status = self.Status.ACKNOWLEDGED
            self.acknowledged_at = timezone.now()
            self.save(update_fields=['status', 'acknowledged_at', 'updated_at'])

    def resolve(self):
        """Mark alert as resolved."""
        from django.utils import timezone
        if self.status != self.Status.RESOLVED:
            self.status = self.Status.RESOLVED
            self.resolved_at = timezone.now()
            self.save(update_fields=['status', 'resolved_at', 'updated_at'])

    def is_new(self):
        """Check if alert is new."""
        return self.status == self.Status.NEW

    def is_critical(self):
        """Check if alert is critical level."""
        return self.level == self.Level.CRITICAL

    @staticmethod
    def create_performance_alert(student, message, level='medium'):
        """Create a performance-related alert."""
        return Alert.objects.create(
            student=student,
            type=Alert.AlertType.PERFORMANCE,
            level=level,
            message=message
        )

    @staticmethod
    def create_attendance_alert(student, message, level='medium'):
        """Create an attendance-related alert."""
        return Alert.objects.create(
            student=student,
            type=Alert.AlertType.ATTENDANCE,
            level=level,
            message=message
        )

    @staticmethod
    def create_risk_alert(student, message, level='high'):
        """Create a risk-related alert."""
        return Alert.objects.create(
            student=student,
            type=Alert.AlertType.RISK,
            level=level,
            message=message
        )

    @staticmethod
    def create_prediction_alert(student, message, level='medium'):
        """Create a prediction-related alert."""
        return Alert.objects.create(
            student=student,
            type=Alert.AlertType.PREDICTION,
            level=level,
            message=message
        )


class Intervention(models.Model):
    """Intervention model - Represents pedagogical interventions for students."""

    class InterventionType(models.TextChoices):
        """Intervention type choices."""
        MEETING = 'meeting', _('Entretien individuel')
        TUTORING = 'tutoring', _('Tutorat')
        ALERT = 'alert', _('Alerte précoce')
        EMAIL = 'email', _('Email de suivi')
        PHONE = 'phone', _('Appel téléphonique')
        PARENT_CONTACT = 'parent_contact', _('Contact parents')
        ACADEMIC_SUPPORT = 'academic_support', _('Soutien académique')
        OTHER = 'other', _('Autre')

    class Priority(models.TextChoices):
        """Priority choices."""
        LOW = 'low', _('Faible')
        MEDIUM = 'medium', _('Moyenne')
        HIGH = 'high', _('Haute')
        URGENT = 'urgent', _('Urgente')

    class Status(models.TextChoices):
        """Intervention status choices."""
        PLANNED = 'planned', _('Planifiée')
        IN_PROGRESS = 'in_progress', _('En cours')
        COMPLETED = 'completed', _('Terminée')
        CANCELLED = 'cancelled', _('Annulée')

    # Intervention Information
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='interventions',
        verbose_name=_('student')
    )
    alert = models.ForeignKey(
        'Alert',
        on_delete=models.SET_NULL,
        related_name='interventions',
        verbose_name=_('related alert'),
        null=True,
        blank=True
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=InterventionType.choices,
        db_index=True
    )
    priority = models.CharField(
        _('priority'),
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
        db_index=True
    )
    description = models.TextField(_('description'))
    
    # Scheduling
    scheduled_date = models.DateField(_('scheduled date'))
    completed_date = models.DateField(_('completed date'), null=True, blank=True)
    
    # Responsible person
    responsible = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='interventions',
        verbose_name=_('responsible'),
        null=True,
        blank=True
    )
    
    # Notes and follow-up
    notes = models.TextField(_('notes'), blank=True)
    outcome = models.TextField(_('outcome'), blank=True)

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'interventions'
        verbose_name = _('intervention')
        verbose_name_plural = _('interventions')
        ordering = ['-scheduled_date', '-created_at']
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['type', 'priority']),
            models.Index(fields=['scheduled_date']),
            models.Index(fields=['responsible', 'status']),
        ]

    def __str__(self):
        return f"{self.get_type_display()} - {self.student.get_full_name()} - {self.scheduled_date}"

    @property
    def student_name(self):
        """Return the student's full name."""
        return self.student.get_full_name() if self.student else None

    @property
    def responsible_name(self):
        """Return the responsible person's full name."""
        return self.responsible.get_full_name() if self.responsible else None

    def complete(self, outcome=''):
        """Mark intervention as completed."""
        from django.utils import timezone
        self.status = self.Status.COMPLETED
        self.completed_date = timezone.now().date()
        if outcome:
            self.outcome = outcome
        self.save()
        
        # Resolve related alert if exists
        if self.alert and self.alert.status != Alert.Status.RESOLVED:
            self.alert.resolve()

    def cancel(self):
        """Cancel the intervention."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=['status', 'updated_at'])
