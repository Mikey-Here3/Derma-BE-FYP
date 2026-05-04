from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from doctors.models import DoctorProfile
from .models import Appointment
from .serializers import AppointmentSerializer, BookAppointmentSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_appointment(request):
    """Patient books an appointment."""
    serializer = BookAppointmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        doctor = DoctorProfile.objects.get(pk=serializer.validated_data['doctor_id'])
    except DoctorProfile.DoesNotExist:
        return Response({'error': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if slot is available
    exists = Appointment.objects.filter(
        doctor=doctor,
        date=serializer.validated_data['date'],
        time_slot=serializer.validated_data['time_slot'],
        status__in=['pending', 'confirmed']
    ).exists()

    if exists:
        return Response({'error': 'This time slot is no longer available.'}, status=status.HTTP_400_BAD_REQUEST)

    appointment = Appointment.objects.create(
        patient=request.user,
        doctor=doctor,
        date=serializer.validated_data['date'],
        time_slot=serializer.validated_data['time_slot'],
        appointment_type=serializer.validated_data['appointment_type'],
        reason=serializer.validated_data.get('reason', ''),
        notes=serializer.validated_data.get('notes', ''),
    )

    return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def appointment_list(request):
    """List appointments filtered by role."""
    if request.user.role == 'doctor':
        try:
            doctor = DoctorProfile.objects.get(user=request.user)
            appointments = Appointment.objects.filter(doctor=doctor)
        except DoctorProfile.DoesNotExist:
            appointments = Appointment.objects.none()
    else:
        appointments = Appointment.objects.filter(patient=request.user)

    # Optional status filter
    status_filter = request.query_params.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def accept_appointment(request, pk):
    """Doctor accepts an appointment."""
    try:
        appointment = Appointment.objects.get(pk=pk, doctor__user=request.user)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)

    appointment.status = 'confirmed'
    appointment.save()
    return Response(AppointmentSerializer(appointment).data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def reject_appointment(request, pk):
    """Doctor rejects an appointment."""
    try:
        appointment = Appointment.objects.get(pk=pk, doctor__user=request.user)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)

    appointment.status = 'rejected'
    appointment.rejection_reason = request.data.get('reason', '')
    appointment.save()
    return Response(AppointmentSerializer(appointment).data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, pk):
    """Patient cancels an appointment."""
    try:
        appointment = Appointment.objects.get(pk=pk, patient=request.user)
    except Appointment.DoesNotExist:
        return Response({'error': 'Appointment not found.'}, status=status.HTTP_404_NOT_FOUND)

    appointment.status = 'cancelled'
    appointment.save()
    return Response(AppointmentSerializer(appointment).data)
