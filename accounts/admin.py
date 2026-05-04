from django.contrib import admin
from .models import User, OTPVerification

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_verified', 'is_doctor_verified']
    list_filter = ['role', 'is_verified', 'is_doctor_verified']
    search_fields = ['email', 'first_name', 'last_name']

@admin.register(OTPVerification)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp', 'purpose', 'is_used', 'created_at']
