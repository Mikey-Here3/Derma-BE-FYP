from rest_framework import serializers
from .models import DiagnosisResult


class DiagnosisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiagnosisResult
        fields = ['id', 'image', 'is_skin', 'skin_confidence', 'condition',
                  'condition_confidence', 'severity', 'severity_score',
                  'affected_areas', 'recommendations', 'ai_details',
                  'health_score', 'created_at']
        read_only_fields = ['id', 'is_skin', 'skin_confidence', 'condition',
                            'condition_confidence', 'severity', 'severity_score',
                            'affected_areas', 'recommendations', 'ai_details',
                            'health_score', 'created_at']


class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
