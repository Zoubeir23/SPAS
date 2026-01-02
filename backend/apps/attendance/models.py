"""
Attendance models for SPAS.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Attendance(models.Model):
    """Attendance model - Represents student attendance records."""

    class Status(models.TextChoices):
        """Attendance status choices."""
        PRESENT = 'present', _('Présent')
        ABSENT = 'absent', _('Absent')
        LATE = 'late', _('Retard')
        EXCUSED = 'excused', _('Absence justifiée')

    # Attendance Information
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendances',
        verbose_name=_('student')
    )
    subject = models.ForeignKey(
        'programs.Subject',
        on_delete=models.PROTECT,
        related_name='attendances',
        verbose_name=_('subject')
    )
    date = models.DateField(_('date'), db_index=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PRESENT,
        db_index=True
    )
    justification = models.TextField(
        _('justification'),
        blank=True,
        null=True,
        help_text=_('Justification for absence or lateness')
    )

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'attendances'
        verbose_name = _('attendance')
        verbose_name_plural = _('attendances')
        ordering = ['-date', 'student']
        unique_together = [['student', 'subject', 'date']]
        indexes = [
            models.Index(fields=['student', 'date']),
            models.Index(fields=['subject', 'date']),
            models.Index(fields=['status', 'date']),
            models.Index(fields=['-date']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.subject.name} - {self.date} - {self.status}"

    @property
    def student_name(self):
        """Return the student's full name."""
        return self.student.get_full_name() if self.student else None

    @property
    def subject_name(self):
        """Return the subject name."""
        return self.subject.name if self.subject else None

    def is_present(self):
        """Check if student was present."""
        return self.status == self.Status.PRESENT

    def is_justified(self):
        """Check if absence/lateness is justified."""
        return self.status == self.Status.EXCUSED or (
            self.justification and self.justification.strip()
        )
