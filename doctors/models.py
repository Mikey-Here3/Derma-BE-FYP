from django.db import models
from django.conf import settings


class DoctorProfile(models.Model):
    SPECIALITY_CHOICES = [
        ('dermatologist', 'Dermatologist'),
        ('cosmetic_dermatologist', 'Cosmetic Dermatologist'),
        ('pediatric_dermatologist', 'Pediatric Dermatologist'),
        ('dermatopathologist', 'Dermatopathologist'),
        ('skin_specialist', 'Skin Specialist'),
        ('general_practice', 'General Practice'),
    ]
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile')
    pmdc_number = models.CharField(max_length=20, blank=True)
    speciality = models.CharField(max_length=30, choices=SPECIALITY_CHOICES, default='dermatologist')
    clinic_address = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bio = models.TextField(blank=True)
    rating = models.FloatField(default=0.0)
    total_reviews = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)

    # Verification documents
    certificate = models.FileField(upload_to='doctor_docs/certificates/', blank=True, null=True)
    id_card = models.FileField(upload_to='doctor_docs/id_cards/', blank=True, null=True)
    clinic_proof = models.FileField(upload_to='doctor_docs/clinic_proofs/', blank=True, null=True)
    verification_status = models.CharField(max_length=10, choices=VERIFICATION_STATUS, default='pending')
    verification_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.user.full_name} - {self.get_speciality_display()}"


class DoctorAvailability(models.Model):
    DAY_CHOICES = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.IntegerField(default=30, help_text='Duration in minutes')

    class Meta:
        unique_together = ['doctor', 'day_of_week', 'start_time']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
