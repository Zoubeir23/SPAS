"""
Student models for SPAS.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Student(models.Model):
    """Student model - Represents a student in the system."""

    class Status(models.TextChoices):
        """Student status choices."""
        ACTIVE = 'active', _('Actif')
        INACTIVE = 'inactive', _('Inactif')
        GRADUATED = 'graduated', _('Diplômé')

    class RiskLevel(models.TextChoices):
        """Student risk level choices."""
        LOW = 'low', _('Faible')
        MEDIUM = 'medium', _('Moyen')
        HIGH = 'high', _('Élevé')
        CRITICAL = 'critical', _('Critique')

    class Level(models.TextChoices):
        """Student academic level choices."""
        L1 = 'L1', _('Licence 1')
        L2 = 'L2', _('Licence 2')
        L3 = 'L3', _('Licence 3')
        M1 = 'M1', _('Master 1')
        M2 = 'M2', _('Master 2')

    # Personal Information
    matricule = models.CharField(
        _('matricule'),
        max_length=50,
        unique=True,
        db_index=True,
        help_text=_('Unique student identification number')
    )
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    email = models.EmailField(_('email'), unique=True, db_index=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'))
    photo = models.ImageField(
        _('photo'),
        upload_to='student_photos/',
        blank=True,
        null=True,
        help_text=_('Student profile picture')
    )

    # Academic Information
    program = models.ForeignKey(
        'programs.Program',
        on_delete=models.PROTECT,
        related_name='students',
        verbose_name=_('program'),
        help_text=_('Academic program the student is enrolled in')
    )
    session = models.ForeignKey(
        'academic_sessions.Session',
        on_delete=models.PROTECT,
        related_name='students',
        verbose_name=_('session'),
        help_text=_('Academic session the student is enrolled in')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True
    )
    level = models.CharField(
        _('level'),
        max_length=5,
        choices=Level.choices,
        default=Level.L1,
        db_index=True,
        help_text=_('Academic level (L1, L2, L3, M1, M2)')
    )

    # Risk Assessment (from ML predictions)
    risk_level = models.CharField(
        _('risk level'),
        max_length=20,
        choices=RiskLevel.choices,
        blank=True,
        null=True,
        db_index=True,
        help_text=_('Predicted risk level for student success')
    )
    risk_score = models.IntegerField(
        _('risk score'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
        help_text=_('Risk score between 0-100 (higher = more at risk)')
    )

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'students'
        verbose_name = _('student')
        verbose_name_plural = _('students')
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['matricule']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['program', 'session']),
        ]

    def __str__(self):
        return f"{self.matricule} - {self.get_full_name()}"

    def get_full_name(self):
        """Return full name of the student."""
        return f"{self.first_name} {self.last_name}"

    @property
    def program_name(self):
        """Return the program name."""
        return self.program.name if self.program else None

    @property
    def session_name(self):
        """Return the session name."""
        return self.session.name if self.session else None

    def update_risk_assessment(self, risk_score, risk_level):
        """Update risk assessment for this student."""
        self.risk_score = risk_score
        self.risk_level = risk_level
        self.save(update_fields=['risk_score', 'risk_level', 'updated_at'])
