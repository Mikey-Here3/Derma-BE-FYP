from django.contrib import admin
from .models import DiagnosisResult

@admin.register(DiagnosisResult)
class DiagnosisResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'condition', 'severity', 'health_score', 'created_at']
    list_filter = ['condition', 'severity']
