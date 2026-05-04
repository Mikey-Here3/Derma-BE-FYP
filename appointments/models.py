from django.db import models
from django.conf import settings


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]
    TYPE_CHOICES = [
        ('in_person', 'In-Person'),
        ('video', 'Video Call'),
    ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_appointments')
    doctor = models.ForeignKey('doctors.DoctorProfile', on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateField()
    time_slot = models.TimeField()
    appointment_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='in_person')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    reason = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time_slot']
        unique_together = ['doctor', 'date', 'time_slot']

    def __str__(self):
        return f"{self.patient.full_name} → Dr. {self.doctor.user.full_name} on {self.date} at {self.time_slot}"
