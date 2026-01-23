"""
Prediction models for SPAS.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Prediction(models.Model):
    """Prediction model - Represents ML predictions for student success."""

    class RiskLevel(models.TextChoices):
        """Risk level choices."""
        LOW = 'low', _('Faible')
        MEDIUM = 'medium', _('Moyen')
        HIGH = 'high', _('Élevé')
        CRITICAL = 'critical', _('Critique')

    # Prediction Information
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='predictions',
        verbose_name=_('student')
    )
    model_version = models.ForeignKey(
        'ml.MLModel',
        on_delete=models.SET_NULL,
        related_name='predictions',
        verbose_name=_('ML model version'),
        null=True,
        blank=True,
        help_text=_('ML model used for this prediction. Null if using heuristics.')
    )

    # Risk Assessment
    risk_score = models.IntegerField(
        _('risk score'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Risk score between 0-100 (higher = more at risk)')
    )
    risk_level = models.CharField(
        _('risk level'),
        max_length=20,
        choices=RiskLevel.choices,
        db_index=True
    )
    predicted_success_rate = models.IntegerField(
        _('predicted success rate'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Predicted probability of student success (0-100)')
    )

    # Contributing Factors (stored as JSON)
    factors = models.JSONField(
        _('factors'),
        default=list,
        help_text=_('Array of factors with name and impact: [{"name": "attendance", "impact": 0.45}, ...]')
    )

    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'predictions'
        verbose_name = _('prediction')
        verbose_name_plural = _('predictions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student', '-created_at']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['model_version', '-created_at']),
        ]

    def __str__(self):
        return f"{self.student.get_full_name()} - Risk: {self.risk_level} ({self.risk_score}%) - {self.created_at.strftime('%Y-%m-%d')}"

    @property
    def student_name(self):
        """Return the student's full name."""
        return self.student.get_full_name() if self.student else None

    @property
    def model_version_name(self):
        """Return the model version string."""
        return f"{self.model_version.name} v{self.model_version.version}" if self.model_version else None

    def save(self, *args, **kwargs):
        """Auto-calculate risk level based on risk score."""
        from django.utils import timezone

        # Determine risk level from risk score
        if self.risk_score >= 75:
            self.risk_level = self.RiskLevel.CRITICAL
        elif self.risk_score >= 50:
            self.risk_level = self.RiskLevel.HIGH
        elif self.risk_score >= 25:
            self.risk_level = self.RiskLevel.MEDIUM
        else:
            self.risk_level = self.RiskLevel.LOW

        super().save(*args, **kwargs)

        # Update student's risk assessment using update() to avoid potential circular references
        from apps.students.models import Student
        Student.objects.filter(id=self.student.id).update(
            risk_score=self.risk_score,
            risk_level=self.risk_level,
            updated_at=timezone.now()
        )
        # Refresh the student instance in memory
        self.student.refresh_from_db(fields=['risk_score', 'risk_level', 'updated_at'])

    def get_top_factors(self, limit=5):
        """Get top N contributing factors sorted by impact."""
        if not self.factors:
            return []
        # Sort factors by impact (descending)
        sorted_factors = sorted(
            self.factors,
            key=lambda x: abs(x.get('impact', 0)),
            reverse=True
        )
        return sorted_factors[:limit]
