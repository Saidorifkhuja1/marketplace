# views.py
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Product, Category
from .serializers import (
    ProductSerializer, ProductCommentSerializer,
    ProductCreateUpdateSerializer, CategorySerializer
)
from user.permissions import IsSeller, IsAdmin


# Category Views
class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class CategoryRetrieveView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'uid'


class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    lookup_field = 'uid'


class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdmin]
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
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()

        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__uid=category)

        # Filter by status if provided
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by owner if provided
        owner = self.request.query_params.get('owner')
        if owner:
            queryset = queryset.filter(owner__uid=owner)

        return queryset.order_by('-created_at')


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
        # Ensure users can only update their own products
        return Product.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)


class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, IsSeller]
    lookup_field = 'uid'

    def get_queryset(self):
        # Ensure users can only delete their own products
        return Product.objects.filter(owner=self.request.user)


class MyProductsListView(generics.ListAPIView):
    """List products belonging to the authenticated user"""
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user).order_by('-created_at')