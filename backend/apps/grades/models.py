"""
Grade models for SPAS.
"""
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _


class Grade(models.Model):
    """Grade model - Represents a student's grade in a subject."""

    class GradeType(models.TextChoices):
        """Grade type choices."""
        EXAM = 'exam', _('Examen')
        ASSIGNMENT = 'assignment', _('Devoir')
        PROJECT = 'project', _('Projet')
        PARTICIPATION = 'participation', _('Participation')

    # Grade Information
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='grades',
        verbose_name=_('student')
    )
    subject = models.ForeignKey(
        'programs.Subject',
        on_delete=models.PROTECT,
        related_name='grades',
        verbose_name=_('subject')
    )
    session = models.ForeignKey(
        'academic_sessions.Session',
        on_delete=models.PROTECT,
        related_name='grades',
        verbose_name=_('session')
    )

    # Grade Values
    value = models.DecimalField(
        _('value'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Grade value obtained by student')
    )
    max_value = models.DecimalField(
        _('max value'),
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Maximum possible grade value')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=GradeType.choices,
        db_index=True
    )
    date = models.DateField(_('date'))

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'grades'
        verbose_name = _('grade')
        verbose_name_plural = _('grades')
        ordering = ['-date', 'student']
        indexes = [
            models.Index(fields=['student', 'subject']),
            models.Index(fields=['student', 'session']),
            models.Index(fields=['subject', 'session']),
            models.Index(fields=['-date']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.name}: {self.value}/{self.max_value}"

    @property
    def student_name(self):
        """Return the student's full name."""
        return self.student.get_full_name() if self.student else None

    @property
    def subject_name(self):
        """Return the subject name."""
        return self.subject.name if self.subject else None

    @property
    def session_name(self):
        """Return the session name."""
        return self.session.name if self.session else None

    @property
    def percentage(self):
        """Calculate grade as percentage."""
        if self.max_value > 0:
            return (self.value / self.max_value) * 100
        return 0

    def is_passing(self, passing_threshold=60):
        """Check if grade is passing."""
        return self.percentage >= passing_threshold
