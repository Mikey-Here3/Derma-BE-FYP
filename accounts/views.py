from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .serializers import (
    RegisterSerializer, LoginSerializer, VerifyEmailSerializer,
    ResendOTPSerializer, ForgotPasswordSerializer, ResetPasswordSerializer, UserSerializer
)
from .models import OTPVerification

User = get_user_model()


def send_otp_email(user, purpose='email_verify'):
    """Create OTP and send via email."""
    # Invalidate previous OTPs
    OTPVerification.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
    otp_obj = OTPVerification.objects.create(user=user, purpose=purpose)

    subject = 'DermaAssist - Email Verification' if purpose == 'email_verify' else 'DermaAssist - Password Reset'
    message = f'Your verification code is: {otp_obj.otp}\n\nThis code expires in 10 minutes.'
    send_mail(subject, message, 'noreply@dermaassist.ai', [user.email])
    return otp_obj.otp


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    otp = send_otp_email(user, 'email_verify')
    return Response({
        'message': 'Account created. Please verify your email.',
        'email': user.email,
        'role': user.role,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = User.objects.get(email=serializer.validated_data['email'])
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.check_password(serializer.validated_data['password']):
        return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_verified:
        return Response({'error': 'Please verify your email first.', 'needs_verification': True},
                        status=status.HTTP_403_FORBIDDEN)

    if user.role == 'doctor' and not user.is_doctor_verified:
        return Response({
            'error': 'Your doctor account is pending verification.',
            'doctor_pending': True
        }, status=status.HTTP_403_FORBIDDEN)

    refresh = RefreshToken.for_user(user)
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    serializer = VerifyEmailSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = User.objects.get(email=serializer.validated_data['email'])
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    otp_obj = OTPVerification.objects.filter(
        user=user, otp=serializer.validated_data['otp'],
        purpose='email_verify', is_used=False,
        created_at__gte=timezone.now() - timedelta(minutes=10)
    ).first()

    if not otp_obj:
        return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj.is_used = True
    otp_obj.save()
    user.is_verified = True
    user.save()

    refresh = RefreshToken.for_user(user)
    return Response({
        'message': 'Email verified successfully.',
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    serializer = ResendOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = User.objects.get(email=serializer.validated_data['email'])
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Rate limit: 30 seconds
    last_otp = OTPVerification.objects.filter(user=user, purpose='email_verify').order_by('-created_at').first()
    if last_otp and (timezone.now() - last_otp.created_at).seconds < 30:
        return Response({'error': 'Please wait before requesting another code.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    send_otp_email(user, 'email_verify')
    return Response({'message': 'OTP resent successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = User.objects.get(email=serializer.validated_data['email'])
    except User.DoesNotExist:
        # Don't reveal if email exists
        return Response({'message': 'If this email exists, a reset code has been sent.'})

    send_otp_email(user, 'password_reset')
    return Response({'message': 'If this email exists, a reset code has been sent.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    serializer = ResetPasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        user = User.objects.get(email=serializer.validated_data['email'])
    except User.DoesNotExist:
        return Response({'error': 'Invalid request.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj = OTPVerification.objects.filter(
        user=user, otp=serializer.validated_data['otp'],
        purpose='password_reset', is_used=False,
        created_at__gte=timezone.now() - timedelta(minutes=10)
    ).first()

    if not otp_obj:
        return Response({'error': 'Invalid or expired OTP.'}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj.is_used = True
    otp_obj.save()
    user.set_password(serializer.validated_data['new_password'])
    user.save()

    return Response({'message': 'Password reset successfully.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)
