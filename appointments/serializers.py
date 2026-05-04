from rest_framework import serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    patient_avatar = serializers.ImageField(source='patient.avatar', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.full_name', read_only=True)
    doctor_speciality = serializers.CharField(source='doctor.get_speciality_display', read_only=True)
    doctor_avatar = serializers.ImageField(source='doctor.user.avatar', read_only=True)

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'patient_name', 'patient_email', 'patient_avatar',
                  'doctor', 'doctor_name', 'doctor_speciality', 'doctor_avatar',
                  'date', 'time_slot', 'appointment_type', 'status',
                  'notes', 'reason', 'rejection_reason', 'created_at']
        read_only_fields = ['id', 'patient', 'status', 'rejection_reason', 'created_at']


class BookAppointmentSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    date = serializers.DateField()
    time_slot = serializers.TimeField()
    appointment_type = serializers.ChoiceField(choices=['in_person', 'video'], default='in_person')
    reason = serializers.CharField(required=False, default='')
    notes = serializers.CharField(required=False, default='')
