from rest_framework import serializers
from .models import Cart
from product.models import Product
from product.serializers import ProductSerializer




class CartSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_uid = serializers.UUIDField(write_only=True)

    class Meta:
        model = Cart
        fields = ['uid', 'product', 'product_uid', 'added_at']

    def create(self, validated_data):
        product_uid = validated_data.pop('product_uid')
        product = Product.objects.get(uid=product_uid)
        return Cart.objects.create(user=self.context['request'].user, product=product, **validated_data)