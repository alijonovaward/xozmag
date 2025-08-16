from django.contrib import admin
from .models import ReceiptItem, Receipt

# Register your models here.
admin.site.register(ReceiptItem)
admin.site.register(Receipt)

