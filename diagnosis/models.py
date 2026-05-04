from django.db import models
from django.conf import settings


class DiagnosisResult(models.Model):
    SEVERITY_CHOICES = [
        ('none', 'None'), ('mild', 'Mild'), ('moderate', 'Moderate'), ('severe', 'Severe'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='diagnoses')
    image = models.ImageField(upload_to='diagnosis_images/')
    is_skin = models.BooleanField(default=True)
    skin_confidence = models.FloatField(default=0.0)
    condition = models.CharField(max_length=100, blank=True)
    condition_confidence = models.FloatField(default=0.0)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='none')
    severity_score = models.FloatField(default=0.0)
    affected_areas = models.JSONField(default=list, blank=True)
    recommendations = models.JSONField(default=list, blank=True)
    ai_details = models.JSONField(default=dict, blank=True)
    health_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.condition} ({self.severity}) - {self.created_at.strftime('%Y-%m-%d')}"
