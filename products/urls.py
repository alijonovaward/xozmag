from django.urls import path
from .views import (
    ProductListView, ProductDetailView, ProductUpdateView, ProductDeleteView,
ProductCreateView, AddStockView
)

urlpatterns = [
    path('', ProductListView.as_view(), name='products'),
    path('add/', ProductCreateView.as_view(), name='product-add'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='product-edit'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('add-stock/<int:pk>/', AddStockView.as_view(), name='add-stock'),
]
