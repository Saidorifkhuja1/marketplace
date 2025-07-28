# views.py

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import Cart
from .serializers import CartSerializer


class AddToCartView(generics.CreateAPIView):
    serializer_class = CartSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RemoveFromCartView(generics.DestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        product_uid = self.kwargs.get('product_uid')
        return self.get_queryset().get(product__uid=product_uid)


class ListCartView(generics.ListAPIView):
    serializer_class = CartSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)


class SearchCartView(generics.ListAPIView):
    serializer_class = CartSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Cart.objects.filter(
            user=self.request.user,
            product__name__icontains=query
        )



