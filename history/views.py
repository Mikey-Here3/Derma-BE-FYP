from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from diagnosis.models import DiagnosisResult
from diagnosis.serializers import DiagnosisResultSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history_list(request):
    """List all past diagnoses for the current user."""
    diagnoses = DiagnosisResult.objects.filter(user=request.user)
    serializer = DiagnosisResultSerializer(diagnoses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def history_stats(request):
    """Summary stats for current user."""
    diagnoses = DiagnosisResult.objects.filter(user=request.user)
    total_scans = diagnoses.count()

    if total_scans == 0:
        return Response({
            'total_scans': 0,
            'avg_health_score': 0,
            'latest_condition': 'No scans yet',
            'latest_severity': 'none',
            'improvement': 0,
        })

    latest = diagnoses.first()
    avg_score = diagnoses.aggregate(avg=Avg('health_score'))['avg'] or 0

    # Calculate improvement (compare last 2 scans)
    improvement = 0
    if total_scans >= 2:
        scans = list(diagnoses[:2])
        improvement = scans[0].health_score - scans[1].health_score

    return Response({
        'total_scans': total_scans,
        'avg_health_score': round(avg_score),
        'latest_condition': latest.condition,
        'latest_severity': latest.severity,
        'improvement': improvement,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def progress_data(request):
    """Progress tracking data — severity over time."""
    diagnoses = DiagnosisResult.objects.filter(user=request.user).order_by('created_at')

    severity_map = {'none': 0, 'mild': 1, 'moderate': 2, 'severe': 3}
    data_points = []

    for d in diagnoses:
        data_points.append({
            'date': d.created_at.strftime('%Y-%m-%d'),
            'health_score': d.health_score,
            'severity': d.severity,
            'severity_numeric': severity_map.get(d.severity, 0),
            'condition': d.condition,
        })

    return Response({
        'data_points': data_points,
        'total_entries': len(data_points),
    })
