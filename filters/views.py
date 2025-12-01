
from rest_framework import generics
from product.models import Product
from product.serializers import ProductSerializer
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class ProductSearchByNameView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Product.objects.filter(name__icontains=query)




class ProductFilterByCategoryView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    def get_queryset(self):
        category_name = self.request.query_params.get('category', '')
        return Product.objects.filter(category__name__iexact=category_name)


class ProductFilterByLocationView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        location = self.request.query_params.get('location', '')
        return Product.objects.filter(location__icontains=location)




class ProductFilterByCostRangeView(generics.ListAPIView):
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
        ]
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        min_cost = self.request.query_params.get('min')
        max_cost = self.request.query_params.get('max')

        if min_cost is None or max_cost is None:
            raise ValidationError({'detail': 'Both "min" and "max" cost values are required.'})

        try:
            min_cost = float(min_cost)
            max_cost = float(max_cost)
        except ValueError:
            raise ValidationError({'detail': '"min" and "max" must be valid numbers.'})

        if min_cost > max_cost:
            raise ValidationError({'detail': '"min" cannot be greater than "max".'})

        return Product.objects.filter(cost__gte=min_cost, cost__lte=max_cost)


