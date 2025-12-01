
from django.urls import path
from .views import *
urlpatterns = [
    path('products/search/', ProductSearchByNameView.as_view()),
    path('products/filter/category/', ProductFilterByCategoryView.as_view()),
    path('products/filter/location/', ProductFilterByLocationView.as_view()),
    path('products/filter/cost/', ProductFilterByCostRangeView.as_view()),
]



