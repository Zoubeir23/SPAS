"""
Program models for SPAS.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Program(models.Model):
    """Academic program model - Represents a study program/filiere."""

    class Status(models.TextChoices):
        """Program status choices."""
        ACTIVE = 'active', _('Actif')
        INACTIVE = 'inactive', _('Inactif')

    # Program Information
    name = models.CharField(_('name'), max_length=200)
    code = models.CharField(
        _('code'),
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_('Unique program code')
    )
    description = models.TextField(_('description'), blank=True, null=True)
    duration = models.IntegerField(
        _('duration (years)'),
        validators=[MinValueValidator(1)],
        help_text=_('Program duration in years')
    )
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
        db_table = 'programs'
        verbose_name = _('program')
        verbose_name_plural = _('programs')
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def student_count(self):
        """Return the number of active students in this program."""
        return self.students.filter(status='active').count()

    def get_active_students(self):
        """Return queryset of active students in this program."""
        return self.students.filter(status='active')


class Subject(models.Model):
    """Subject/Course model - Represents a matiere/subject taught in programs."""

    # Subject Information
    name = models.CharField(_('name'), max_length=200)
    code = models.CharField(
        _('code'),
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_('Unique subject code')
    )
    description = models.TextField(_('description'), blank=True, null=True)

    # Relations
    programs = models.ManyToManyField(
        Program,
        related_name='subjects',
        verbose_name=_('programs'),
        help_text=_('Programs that include this subject')
    )

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'subjects'
        verbose_name = _('subject')
        verbose_name_plural = _('subjects')
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
