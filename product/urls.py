# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Category URLs
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category-create'),
    path('categories/<uuid:uid>/', views.CategoryRetrieveView.as_view(), name='category-detail'),
    path('categories/<uuid:uid>/update/', views.CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<uuid:uid>/delete/', views.CategoryDeleteView.as_view(), name='category-delete'),

    # Product URLs
    path('products/', views.ProductListAPIView.as_view(), name='product-list'),
    path('products/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('products/<uuid:uid>/', views.ProductRetrieveView.as_view(), name='product-detail'),
    path('products/<uuid:uid>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('products/<uuid:uid>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),

    # My products
    path('my-products/', views.MyProductsListView.as_view(), name='my-products'),
]
