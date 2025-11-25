from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import PermissionDenied

from .models import Product, Category
from .serializers import *
from user.permissions import IsSeller, IsAdmin


# ============================
#        CATEGORY VIEWS
# ============================

class CategoryCreateView(generics.CreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [IsAdmin]


class CategoryRetrieveView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'uid'
    # permission_classes = [IsAdmin]


class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'uid'
    # permission_classes = [IsAdmin]


class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'uid'
    # permission_classes = [IsAdmin]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



# ============================
#        PRODUCT VIEWS
# ============================

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # Photos are saved directly (NO TEMP, NO FINALIZE)
        serializer.save(owner=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({"message": "Product created successfully"}, status=status.HTTP_201_CREATED)



class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter
    ]

    filterset_fields = ['category', 'owner', 'location']
    search_fields = ['name', 'description', 'location']
    ordering_fields = ['created_at', 'updated_at', 'cost', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        return Product.objects.filter(
            status='active'
        ).select_related('owner', 'category').order_by('-created_at')

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response({
                'products': serializer.data,
                'total_count': queryset.count(),
                'timestamp': timezone.now().isoformat(),
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'products': serializer.data,
            'total_count': queryset.count(),
            'timestamp': timezone.now().isoformat(),
        })



class ProductRetrieveView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer   # NO COMMENTS ANYMORE
    lookup_field = 'uid'



class ProductUpdateView(generics.UpdateAPIView):
    serializer_class = ProductCreateUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'uid'
    # permission_classes = [IsAuthenticated, IsSeller]

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)



class ProductDeleteView(generics.DestroyAPIView):
    serializer_class = ProductSerializer
    lookup_field = 'uid'
    # permission_classes = [IsAuthenticated, IsSeller]

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)



class MyProductsListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(
            owner=self.request.user
        ).order_by('-created_at')



# class PendingProductListView(generics.ListAPIView):
#     serializer_class = ProductListSerializer
#     # permission_classes = [IsAdmin]
#
#     def get_queryset(self):
#         return Product.objects.filter(status='pending')



# ============================
#   ADMIN: STATUS UPDATE
# ============================

# class ProductStatusUpdateView(generics.UpdateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductStatusUpdateSerializer
#     lookup_field = 'uid'
#     # permission_classes = [IsAdmin]
#
#     def perform_update(self, serializer):
#         if serializer.validated_data.get('status') != 'active':
#             raise PermissionDenied("You can only set status to 'active'.")
#         serializer.save()

