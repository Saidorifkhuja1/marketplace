from django.urls import path
from .views import *
urlpatterns = [
    path('category/create/', CategoryCreateView.as_view()),
    path('category/<uuid:uid>/', CategoryRetrieveView.as_view()),
    path('category/<uuid:uid>/update/', CategoryUpdateView.as_view()),
    path('category/<uuid:uid>/delete/', CategoryDeleteView.as_view()),

    # path('product/create/', ProductCreateView.as_view()),
    path('product/list/', ProductListAPIView.as_view()),
    path('product_details/<uuid:uid>/', ProductRetrieveView.as_view()),
    path('product/<uuid:uid>/update/', ProductUpdateView.as_view()),
    path('product/<uuid:uid>/delete/', ProductDeleteView.as_view()),



]


