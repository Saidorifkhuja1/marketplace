# urls.py
from django.urls import path
from product.views import (
    CategoryListView,
    CategoryCreateView,
    CategoryRetrieveView,
    CategoryUpdateView,
    CategoryDeleteView,
    ProductListAPIView,
    ProductCreateView,
    ProductRetrieveView,
    ProductUpdateView,
    ProductDeleteView,
    MyProductsListView,
    PendingProductListView,
    ProductStatusUpdateView,
)

urlpatterns = [

    path('categories/', CategoryListView.as_view()),
    path('categories/create/', CategoryCreateView.as_view()),
    path('categories/<uuid:uid>/', CategoryRetrieveView.as_view()),
    path('categories/<uuid:uid>/update/', CategoryUpdateView.as_view()),
    path('categories/<uuid:uid>/delete/', CategoryDeleteView.as_view()),


    path('products/', ProductListAPIView.as_view()),
    path('products/create/', ProductCreateView.as_view()),
    path('products/<uuid:uid>/', ProductRetrieveView.as_view()),
    path('products/<uuid:uid>/update/', ProductUpdateView.as_view()),
    path('products/<uuid:uid>/delete/', ProductDeleteView.as_view()),


    path('my-products/', MyProductsListView.as_view()),

    path('admin/products/pending/', PendingProductListView.as_view()),
    path('update_status/<uuid:uid>/', ProductStatusUpdateView.as_view()),
]
