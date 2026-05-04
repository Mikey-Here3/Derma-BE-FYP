from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db.models import Q
from .models import DoctorProfile, DoctorAvailability
from .serializers import (
    DoctorListSerializer, DoctorDetailSerializer,
    DoctorVerificationSerializer, DoctorAvailabilitySerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def doctor_list(request):
    """List verified doctors with search/filter."""
    doctors = DoctorProfile.objects.filter(verification_status='approved', user__is_active=True)

    # Search
    search = request.query_params.get('search', '')
    if search:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(user__city__icontains=search)
        )

    # Filter by city
    city = request.query_params.get('city', '')
    if city:
        doctors = doctors.filter(user__city__icontains=city)

    # Filter by speciality
    speciality = request.query_params.get('speciality', '')
    if speciality:
        doctors = doctors.filter(speciality=speciality)

    # Filter by availability
    available = request.query_params.get('available', '')
    if available == 'true':
        doctors = doctors.filter(is_available=True)

    serializer = DoctorListSerializer(doctors, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def doctor_detail(request, pk):
    """Get doctor profile with availability."""
    try:
        doctor = DoctorProfile.objects.get(pk=pk, verification_status='approved')
    except DoctorProfile.DoesNotExist:
        return Response({'error': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = DoctorDetailSerializer(doctor)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def submit_verification(request):
    """Doctor submits verification documents."""
    if request.user.role != 'doctor':
        return Response({'error': 'Only doctors can submit verification.'}, status=status.HTTP_403_FORBIDDEN)

    profile, created = DoctorProfile.objects.get_or_create(user=request.user)
    serializer = DoctorVerificationSerializer(profile, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(verification_status='pending')

    return Response({'message': 'Verification documents submitted. Review takes 24-48 hours.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verification_status(request):
    """Check own doctor verification status."""
    if request.user.role != 'doctor':
        return Response({'error': 'Not a doctor account.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        profile = DoctorProfile.objects.get(user=request.user)
        return Response({
            'status': profile.verification_status,
            'notes': profile.verification_notes,
        })
    except DoctorProfile.DoesNotExist:
        return Response({'status': 'not_submitted'})


@api_view(['GET'])
@permission_classes([AllowAny])
def doctor_slots(request, pk):
    """Get available time slots for a doctor."""
    try:
        doctor = DoctorProfile.objects.get(pk=pk)
    except DoctorProfile.DoesNotExist:
        return Response({'error': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)

    availability = DoctorAvailability.objects.filter(doctor=doctor)
    serializer = DoctorAvailabilitySerializer(availability, many=True)
    return Response(serializer.data)
