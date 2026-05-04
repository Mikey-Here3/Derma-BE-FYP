from django.db import models
from django.conf import settings


class PatientProfile(models.Model):
    SKIN_TYPE_CHOICES = [
        ('oily', 'Oily'), ('dry', 'Dry'), ('combination', 'Combination'),
        ('normal', 'Normal'), ('sensitive', 'Sensitive'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    skin_type = models.CharField(max_length=20, choices=SKIN_TYPE_CHOICES, blank=True, default='')
    date_of_birth = models.DateField(null=True, blank=True)
    allergies = models.TextField(blank=True, default='')
    medical_notes = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Profile: {self.user.email}"
