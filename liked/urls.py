# urls.py

from django.urls import path
from .views import AddToCartView, RemoveFromCartView, ListCartView, SearchCartView

urlpatterns = [
    path('cart/add/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/remove/<uuid:product_uid>/', RemoveFromCartView.as_view(), name='remove-from-cart'),
    path('car_list/', ListCartView.as_view(), name='list-cart'),
    path('cart/search/', SearchCartView.as_view(), name='search-cart'),
]