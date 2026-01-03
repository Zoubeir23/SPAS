"""
Program models for SPAS.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Department(models.Model):
    """Department model - Represents an academic department (Département)."""

    class Status(models.TextChoices):
        """Department status choices."""
        ACTIVE = 'active', _('Actif')
        INACTIVE = 'inactive', _('Inactif')

    # Department Information
    name = models.CharField(
        _('name'),
        max_length=200,
        unique=True,
        db_index=True,
        help_text=_('Department name (e.g., "Département Réseaux et Systèmes")')
    )
    code = models.CharField(
        _('code'),
        max_length=20,
        unique=True,
        db_index=True,
        help_text=_('Unique department code (e.g., "DRS", "DGI")')
    )
    description = models.TextField(_('description'), blank=True, null=True)
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
        db_table = 'departments'
        verbose_name = _('department')
        verbose_name_plural = _('departments')
        ordering = ['code']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def program_count(self):
        """Return the number of active programs in this department."""
        return self.programs.filter(status='active').count()

    def get_active_programs(self):
        """Return queryset of active programs in this department."""
        return self.programs.filter(status='active')


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

    # Department Relation
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='programs',
        verbose_name=_('department'),
        help_text=_('Academic department this program belongs to'),
        null=True,
        blank=True  # Allow null for backward compatibility during migration
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
            models.Index(fields=['department']),
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
