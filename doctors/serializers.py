from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DoctorProfile, DoctorAvailability

User = get_user_model()


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = DoctorAvailability
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'slot_duration']


class DoctorListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    city = serializers.CharField(source='user.city', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    speciality_display = serializers.CharField(source='get_speciality_display', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = DoctorProfile
        fields = ['id', 'user_id', 'full_name', 'avatar', 'email', 'city',
                  'speciality', 'speciality_display', 'experience_years',
                  'consultation_fee', 'rating', 'total_reviews', 'is_available',
                  'clinic_address', 'bio']


class DoctorDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    avatar = serializers.ImageField(source='user.avatar', read_only=True)
    city = serializers.CharField(source='user.city', read_only=True)
    phone = serializers.CharField(source='user.phone', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    speciality_display = serializers.CharField(source='get_speciality_display', read_only=True)
    availability = DoctorAvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = DoctorProfile
        fields = ['id', 'full_name', 'avatar', 'email', 'phone', 'city',
                  'speciality', 'speciality_display', 'experience_years',
                  'consultation_fee', 'rating', 'total_reviews', 'is_available',
                  'clinic_address', 'bio', 'pmdc_number', 'availability',
                  'verification_status']


class DoctorVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = ['pmdc_number', 'speciality', 'clinic_address', 'certificate',
                  'id_card', 'clinic_proof', 'bio', 'experience_years', 'consultation_fee']
