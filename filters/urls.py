from django.urls import path
from . import views

urlpatterns = [
    path('products/filter/category/', views.filter_by_category),
    path('products/filter/location/', views.filter_by_location),
    path('products/filter/price/', views.filter_by_price),
    path('products/search/', views.search_products),
]


