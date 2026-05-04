from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from doctors.models import DoctorProfile
from doctors.serializers import DoctorDetailSerializer
from diagnosis.models import DiagnosisResult
from appointments.models import Appointment
from accounts.serializers import UserSerializer
from .permissions import IsAdmin

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAdmin])
def dashboard_stats(request):
    """Admin dashboard stats."""
    total_patients = User.objects.filter(role='patient').count()
    total_doctors = User.objects.filter(role='doctor').count()
    pending_verifications = DoctorProfile.objects.filter(verification_status='pending').count()
    approved_doctors = DoctorProfile.objects.filter(verification_status='approved').count()
    total_diagnoses = DiagnosisResult.objects.count()
    total_appointments = Appointment.objects.count()
    active_users = User.objects.filter(is_active=True).count()

    return Response({
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'pending_verifications': pending_verifications,
        'approved_doctors': approved_doctors,
        'total_diagnoses': total_diagnoses,
        'total_appointments': total_appointments,
        'active_users': active_users,
    })


@api_view(['GET'])
@permission_classes([IsAdmin])
def patient_list(request):
    """List all patients."""
    patients = User.objects.filter(role='patient')
    search = request.query_params.get('search', '')
    if search:
        patients = patients.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )
    serializer = UserSerializer(patients, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdmin])
def patient_detail(request, pk):
    """Patient detail with diagnosis history."""
    try:
        patient = User.objects.get(pk=pk, role='patient')
    except User.DoesNotExist:
        return Response({'error': 'Patient not found.'}, status=status.HTTP_404_NOT_FOUND)

    from diagnosis.serializers import DiagnosisResultSerializer
    diagnoses = DiagnosisResult.objects.filter(user=patient)

    return Response({
        'user': UserSerializer(patient).data,
        'diagnoses': DiagnosisResultSerializer(diagnoses, many=True).data,
        'total_scans': diagnoses.count(),
    })


@api_view(['GET'])
@permission_classes([IsAdmin])
def pending_doctors(request):
    """List pending doctor verifications."""
    pending = DoctorProfile.objects.filter(verification_status='pending')
    serializer = DoctorDetailSerializer(pending, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdmin])
def doctor_admin_detail(request, pk):
    """Doctor detail with verification documents."""
    try:
        doctor = DoctorProfile.objects.get(pk=pk)
    except DoctorProfile.DoesNotExist:
        return Response({'error': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorDetailSerializer(doctor)
    data = serializer.data
    data['certificate_url'] = doctor.certificate.url if doctor.certificate else None
    data['id_card_url'] = doctor.id_card.url if doctor.id_card else None
    data['clinic_proof_url'] = doctor.clinic_proof.url if doctor.clinic_proof else None
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAdmin])
def approve_doctor(request, pk):
    """Approve a doctor."""
    try:
        doctor = DoctorProfile.objects.get(pk=pk)
    except DoctorProfile.DoesNotExist:
        return Response({'error': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)

    doctor.verification_status = 'approved'
    doctor.verification_notes = request.data.get('notes', 'Approved by admin.')
    doctor.save()

    doctor.user.is_doctor_verified = True
    doctor.user.save()

    return Response({'message': f'Dr. {doctor.user.full_name} has been approved.'})


@api_view(['POST'])
@permission_classes([IsAdmin])
def reject_doctor(request, pk):
    """Reject a doctor."""
    try:
        doctor = DoctorProfile.objects.get(pk=pk)
    except DoctorProfile.DoesNotExist:
        return Response({'error': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)

    doctor.verification_status = 'rejected'
    doctor.verification_notes = request.data.get('reason', 'Rejected by admin.')
    doctor.save()

    return Response({'message': f'Dr. {doctor.user.full_name} has been rejected.'})


@api_view(['POST'])
@permission_classes([IsAdmin])
def suspend_patient(request, pk):
    """Suspend a patient account."""
    try:
        patient = User.objects.get(pk=pk, role='patient')
    except User.DoesNotExist:
        return Response({'error': 'Patient not found.'}, status=status.HTTP_404_NOT_FOUND)

    patient.is_active = not patient.is_active
    patient.save()

    action = 'suspended' if not patient.is_active else 'reactivated'
    return Response({'message': f'Patient {patient.full_name} has been {action}.'})


@api_view(['GET'])
@permission_classes([IsAdmin])
def analytics(request):
    """System analytics — user growth, disease distribution."""
    # User growth by month
    user_growth = User.objects.annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(count=Count('id')).order_by('month')

    # Disease distribution
    disease_dist = DiagnosisResult.objects.values('condition').annotate(
        count=Count('id')
    ).order_by('-count')

    # Severity distribution
    severity_dist = DiagnosisResult.objects.values('severity').annotate(
        count=Count('id')
    ).order_by('severity')

    return Response({
        'user_growth': list(user_growth),
        'disease_distribution': list(disease_dist),
        'severity_distribution': list(severity_dist),
    })
