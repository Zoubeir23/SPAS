"""
Session models for SPAS.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Session(models.Model):
    """Academic session model - Represents a school year/semester session."""

    class Status(models.TextChoices):
        """Session status choices."""
        ACTIVE = 'active', _('Actif')
        INACTIVE = 'inactive', _('Inactif')
        COMPLETED = 'completed', _('Terminé')

    # Session Information
    name = models.CharField(_('name'), max_length=100, db_index=True)
    year = models.CharField(_('year'), max_length=20, help_text=_('Academic year (e.g., 2023-2024)'))
    start_date = models.DateField(_('start date'))
    end_date = models.DateField(_('end date'))
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'sessions'
        verbose_name = _('session')
        verbose_name_plural = _('sessions')
        ordering = ['-year', '-start_date']
        indexes = [
            models.Index(fields=['year']),
            models.Index(fields=['status']),
            models.Index(fields=['-start_date']),
        ]
        unique_together = [['name', 'year']]

    def __str__(self):
        return f"{self.name} ({self.year})"

    @property
    def student_count(self):
        """Return the number of active students in this session."""
        return self.students.filter(status='active').count()

    def is_current(self):
        """Check if this session is currently active."""
        from django.utils import timezone
        now = timezone.now().date()
        return self.start_date <= now <= self.end_date and self.status == 'active'

    def get_active_students(self):
        """Return queryset of active students in this session."""
        return self.students.filter(status='active')
