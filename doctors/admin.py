from django.contrib import admin
from .models import DoctorProfile, DoctorAvailability

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'speciality', 'verification_status', 'rating']
    list_filter = ['verification_status', 'speciality']

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time']
