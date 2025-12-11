from django.urls import path
from .views import (
    CommentCreateView,
    CommentUpdateView,
    CommentDeleteView,
    MyCommentsListView,
    ProductCommentsListView
)

urlpatterns = [
    path('create/', CommentCreateView.as_view(), name='comment-create'),
    path('<uuid:uid>/update/', CommentUpdateView.as_view(), name='comment-update'),
    path('<uuid:uid>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
    path('my/', MyCommentsListView.as_view(), name='my-comments'),
    path('product/<uuid:uid>/', ProductCommentsListView.as_view(), name='product-comments'),
]