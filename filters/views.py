from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from product.models import Product
from product.serializers import ProductSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from product.models import Product
from product.serializers import ProductSerializer


# ============================
#   FILTER BY CATEGORY
# ============================
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'category',
            openapi.IN_QUERY,
            description="Kategoriya nomi bo‘yicha filter",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: ProductSerializer(many=True)}
)
@api_view(['GET'])
def filter_by_category(request):
    category = request.GET.get('category')
    if not category:
        return Response({"error": "category parametri kerak"}, status=400)

    products = Product.objects.filter(category__name__icontains=category)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=200)


# ============================
#   FILTER BY LOCATION
# ============================
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'location',
            openapi.IN_QUERY,
            description="Manzil bo‘yicha filter (masalan: Namangan)",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: ProductSerializer(many=True)}
)
@api_view(['GET'])
def filter_by_location(request):
    location = request.GET.get('location')
    if not location:
        return Response({"error": "location parametri kerak"}, status=400)

    products = Product.objects.filter(location__icontains=location)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=200)


# ============================
#   FILTER BY PRICE RANGE
# ============================
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'min',
            openapi.IN_QUERY,
            description="Minimum narx",
            type=openapi.TYPE_INTEGER
        ),
        openapi.Parameter(
            'max',
            openapi.IN_QUERY,
            description="Maksimum narx",
            type=openapi.TYPE_INTEGER
        ),
    ],
    responses={200: ProductSerializer(many=True)}
)
@api_view(['GET'])
def filter_by_price(request):
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')

    if not min_price or not max_price:
        return Response({"error": "min va max parametrlari kerak"}, status=400)

    products = Product.objects.filter(
        cost__gte=min_price,
        cost__lte=max_price
    )

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=200)


# ============================
#   SEARCH BY NAME
# ============================
@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'query',
            openapi.IN_QUERY,
            description="Mahsulot nomi bo‘yicha qidiruv",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={200: ProductSerializer(many=True)}
)
@api_view(['GET'])
def search_products(request):
    query = request.GET.get('query')
    if not query:
        return Response({"error": "query parametri kerak"}, status=400)

    products = Product.objects.filter(name__icontains=query)
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data, status=200)