from django.urls import path
from . import views

urlpatterns = [
    path('', views.sales_page, name='sales_page'),
    path('api/search/', views.product_search_api, name='product_search_api'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/close/', views.close_cart, name='close_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
]
