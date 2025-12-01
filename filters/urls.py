from django.urls import path
from .views import (
    ProductSearchByNameView,
    ProductFilterByCategoryView,
    ProductFilterByLocationView,
    ProductFilterByCostRangeView
)

app_name = 'filters'

urlpatterns = [
    path('products/search/', ProductSearchByNameView.as_view(), name='product-search'),
    path('products/filter/category/', ProductFilterByCategoryView.as_view(), name='filter-by-category'),
    path('products/filter/location/', ProductFilterByLocationView.as_view(), name='filter-by-location'),
    path('products/filter/cost/', ProductFilterByCostRangeView.as_view(), name='filter-by-cost'),
]



