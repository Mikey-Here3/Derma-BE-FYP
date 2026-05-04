from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from diagnosis.models import DiagnosisResult


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def product_list(request):
    """List all active products."""
    products = Product.objects.filter(is_active=True)
    category = request.query_params.get('category', '')
    if category:
        products = products.filter(category=category)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_products(request):
    """Get personalized product recommendations based on latest diagnosis."""
    latest = DiagnosisResult.objects.filter(user=request.user).first()

    if not latest:
        products = Product.objects.filter(is_active=True)[:6]
    else:
        # Filter by condition match
        products = Product.objects.filter(
            is_active=True,
            conditions__contains=[latest.condition]
        )
        if not products.exists():
            products = Product.objects.filter(is_active=True)[:6]

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
