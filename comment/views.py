from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Comment
from .serializers import CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer
from product.models import Product


class CommentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class CommentUpdateView(generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    def get_queryset(self):
        return Comment.objects.filter(owner=self.request.user)


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uid'

    def get_queryset(self):
        return Comment.objects.filter(owner=self.request.user)


class MyCommentsListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination

    def get_queryset(self):
        return Comment.objects.filter(owner=self.request.user)


class ProductCommentsListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    lookup_field = 'uid'

    def get_queryset(self):
        product_uid = self.kwargs.get('uid')
        return Comment.objects.filter(product__uid=product_uid)