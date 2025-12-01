from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from product.models import Product
from product.serializers import ProductSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ProductSearchByNameView(generics.ListAPIView):
    """
    Product nomini qidirish
    Query param: q (search query)
    Example: /filters/products/search/?q=iphone
    """
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'q', openapi.IN_QUERY,
                description="Search query for product name",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        operation_description="Search products by name (case-insensitive)"
    )
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        if not query:
            return Response(
                {'detail': 'Search query "q" is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Product.objects.filter(name__icontains=query, is_deleted=False)


class ProductFilterByCategoryView(generics.ListAPIView):
    """
    Category bo'yicha filter
    Query param: category (category name)
    Example: /filters/products/filter/category/?category=Electronics
    """
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'category', openapi.IN_QUERY,
                description="Category name for filtering",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        operation_description="Filter products by category name"
    )
    def get(self, request, *args, **kwargs):
        category = request.query_params.get('category', '')
        if not category:
            return Response(
                {'detail': 'Category name is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        category_name = self.request.query_params.get('category', '')
        return Product.objects.filter(
            category__name__iexact=category_name,
            is_deleted=False
        )


class ProductFilterByLocationView(generics.ListAPIView):
    """
    Location bo'yicha filter
    Query param: location (location name)
    Example: /filters/products/filter/location/?location=Tashkent
    """
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'location', openapi.IN_QUERY,
                description="Location for filtering",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        operation_description="Filter products by location"
    )
    def get(self, request, *args, **kwargs):
        location = request.query_params.get('location', '')
        if not location:
            return Response(
                {'detail': 'Location is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        location = self.request.query_params.get('location', '')
        return Product.objects.filter(
            location__icontains=location,
            is_deleted=False
        )


class ProductFilterByCostRangeView(generics.ListAPIView):
    """
    Narx oralig'i bo'yicha filter
    Query params: min, max (cost range)
    Example: /filters/products/filter/cost/?min=100&max=500
    """
    serializer_class = ProductSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'min', openapi.IN_QUERY,
                description="Minimum product cost",
                type=openapi.TYPE_NUMBER,
                required=True
            ),
            openapi.Parameter(
                'max', openapi.IN_QUERY,
                description="Maximum product cost",
                type=openapi.TYPE_NUMBER,
                required=True
            )
        ],
        operation_description="Filter products by cost range"
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        min_cost = self.request.query_params.get('min')
        max_cost = self.request.query_params.get('max')

        if min_cost is None or max_cost is None:
            raise ValidationError({
                'detail': 'Both "min" and "max" cost values are required.'
            })

        try:
            min_cost = float(min_cost)
            max_cost = float(max_cost)
        except ValueError:
            raise ValidationError({
                'detail': '"min" and "max" must be valid numbers.'
            })

        if min_cost < 0 or max_cost < 0:
            raise ValidationError({
                'detail': 'Cost values cannot be negative.'
            })

        if min_cost > max_cost:
            raise ValidationError({
                'detail': '"min" cannot be greater than "max".'
            })

        return Product.objects.filter(
            cost__gte=min_cost,
            cost__lte=max_cost,
            is_deleted=False
        )
