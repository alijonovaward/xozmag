from xml.etree.ElementInclude import include

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('home.urls')),
    path('products/', include('products.urls')),
    path('sales/', include('sale.urls')),
    path('stats/', include('stats.urls')),
    path('returns/', include('returns.urls')),
]
