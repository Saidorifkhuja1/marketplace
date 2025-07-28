from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied
from .models import Product, Category
from .serializers import *
from user.permissions import IsSeller, IsAdmin


# Category Views
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ IsAdmin]


class CategoryRetrieveView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ IsAdmin]
    lookup_field = 'uid'


class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ IsAdmin]
    lookup_field = 'uid'


class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ IsAdmin]
    lookup_field = 'uid'


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# Product Views
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProductListAPIView(generics.ListAPIView):

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['category', 'owner', 'location']
    search_fields = ['name', 'description', 'location']

    ordering_fields = ['created_at', 'updated_at', 'cost', 'name']
    ordering = ['-created_at']

    def get_queryset(self):

        return Product.objects.filter(
            status='active'
        ).select_related(
            'owner', 'category'
        ).order_by('-created_at')

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'products': serializer.data,
                'total_count': queryset.count(),
                'timestamp': timezone.now().isoformat(),  # For real-time sync
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'products': serializer.data,
            'total_count': queryset.count(),
            'timestamp': timezone.now().isoformat(),
        })


class ProductRetrieveView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCommentSerializer
    lookup_field = 'uid'


class ProductUpdateView(generics.UpdateAPIView):
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'uid'

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)




class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsSeller]
    lookup_field = 'uid'

    def get_queryset(self):

        return Product.objects.filter(owner=self.request.user)


class MyProductsListView(generics.ListAPIView):

    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user).order_by('-created_at')


class PendingProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return Product.objects.filter(status='pending')




class ProductStatusUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductStatusUpdateSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'uid'

    def perform_update(self, serializer):
        if serializer.validated_data.get('status') != 'active':
            raise PermissionDenied("You can only set status to 'active'.")
        serializer.save()
