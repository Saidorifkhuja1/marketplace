import os
import shutil
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, filters, status
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
    # permission_classes = [ IsAdmin]


class CategoryRetrieveView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [ IsAdmin]
    lookup_field = 'uid'


class CategoryUpdateView(generics.UpdateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [ IsAdmin]
    lookup_field = 'uid'


class CategoryDeleteView(generics.DestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # permission_classes = [ IsAdmin]
    lookup_field = 'uid'


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# Product Views
# class ProductCreateView(generics.CreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductCreateUpdateSerializer
#     permission_classes = [IsAuthenticated, IsSeller]
#     parser_classes = [MultiPartParser, FormParser]
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        # Save product without any photos
        product = serializer.save(owner=self.request.user)

        # Handle uploaded images
        request_files = self.request.FILES
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_products', str(product.uid))
        os.makedirs(temp_dir, exist_ok=True)

        for i in range(1, 6):
            photo = request_files.get(f'photo{i}')
            if photo:
                ext = os.path.splitext(photo.name)[1]
                filename = f'photo{i}{ext}'
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, 'wb+') as dest:
                    for chunk in photo.chunks():
                        dest.write(chunk)

        return product

    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)
        return Response({
            "message": "Product created. Photos stored temporarily. Must finalize within 5 days."
        }, status=status.HTTP_201_CREATED)


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
    # permission_classes = [IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]
    lookup_field = 'uid'

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)




class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated, IsSeller]
    lookup_field = 'uid'

    def get_queryset(self):

        return Product.objects.filter(owner=self.request.user)


class MyProductsListView(generics.ListAPIView):

    serializer_class = ProductSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user).order_by('-created_at')


class PendingProductListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    # permission_classes = [IsAdmin]

    def get_queryset(self):
        return Product.objects.filter(status='pending')




class ProductStatusUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductStatusUpdateSerializer
    # permission_classes = [IsAdmin]
    lookup_field = 'uid'

    def perform_update(self, serializer):
        if serializer.validated_data.get('status') != 'active':
            raise PermissionDenied("You can only set status to 'active'.")
        serializer.save()



class FinalizeProductView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer  # Only required by DRF; not used in logic
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    def update(self, request, *args, **kwargs):
        uid = kwargs.get('uid')

        try:
            product = self.get_queryset().get(uid=uid, owner=request.user)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=404)

        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_products', str(product.uid))
        if not os.path.exists(temp_dir):
            return Response({"error": "Temp photos not found or expired."}, status=400)

        for i in range(1, 6):
            photo_path = os.path.join(temp_dir, f'photo{i}.jpg')
            if os.path.exists(photo_path):
                new_path = os.path.join('products', f'{product.uid}_photo{i}.jpg')
                full_new_path = os.path.join(settings.MEDIA_ROOT, new_path)
                shutil.move(photo_path, full_new_path)
                setattr(product, f'photo{i}', new_path)

        product.save()
        shutil.rmtree(temp_dir, ignore_errors=True)

        return Response({"message": "Product finalized and photos saved."}, status=200)