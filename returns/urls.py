from django.urls import path
from . import views

urlpatterns = [
    path('return/', views.return_product_page, name='return_page'),
    path('list/', views.returned_list, name='returned_list'),
]
