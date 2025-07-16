
from rest_framework import generics
from product.models import Product
from product.serializers import ProductSerializer


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

    def get_queryset(self):
        min_cost = self.request.query_params.get('min', 0)
        max_cost = self.request.query_params.get('max', 999999999)
        return Product.objects.filter(cost__gte=min_cost, cost__lte=max_cost)
