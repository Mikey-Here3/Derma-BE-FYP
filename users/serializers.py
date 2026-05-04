from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PatientProfile

User = get_user_model()


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['skin_type', 'date_of_birth', 'allergies', 'medical_notes']


class UserProfileSerializer(serializers.ModelSerializer):
    patient_profile = PatientProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name', 'role',
                  'phone', 'city', 'avatar', 'is_verified', 'is_doctor_verified',
                  'latitude', 'longitude', 'patient_profile']
        read_only_fields = ['id', 'email', 'role', 'is_verified', 'is_doctor_verified']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('patient_profile', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data and instance.role == 'patient':
            profile, _ = PatientProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs
