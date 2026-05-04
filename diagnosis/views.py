from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import DiagnosisResult
from .serializers import DiagnosisResultSerializer, ImageUploadSerializer
from .services.ai_service import ai_service


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def analyze(request):
    """Upload skin image and get AI analysis."""
    serializer = ImageUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    image = serializer.validated_data['image']

    # Save diagnosis record with image
    diagnosis = DiagnosisResult.objects.create(user=request.user, image=image)

    # Run AI analysis
    try:
        result = ai_service.analyze(diagnosis.image.path)

        # Update diagnosis with results
        diagnosis.is_skin = result['is_skin']
        diagnosis.skin_confidence = result['skin_confidence']
        diagnosis.condition = result['condition']
        diagnosis.condition_confidence = result['condition_confidence']
        diagnosis.severity = result['severity']
        diagnosis.severity_score = result['severity_score']
        diagnosis.affected_areas = result['affected_areas']
        diagnosis.recommendations = result['recommendations']
        diagnosis.ai_details = result['ai_details']
        diagnosis.health_score = result['health_score']
        diagnosis.save()
    except Exception as e:
        return Response({'error': f'Analysis failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(DiagnosisResultSerializer(diagnosis).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def diagnosis_detail(request, pk):
    """Get a specific diagnosis result."""
    try:
        diagnosis = DiagnosisResult.objects.get(pk=pk, user=request.user)
    except DiagnosisResult.DoesNotExist:
        return Response({'error': 'Diagnosis not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(DiagnosisResultSerializer(diagnosis).data)
