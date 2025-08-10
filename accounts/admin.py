from django.contrib import admin
from .models import Profile

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment', 'phone', 'added_time', 'description', 'ready')
    search_fields = ['user', 'phone']
    list_filter = ['ready']