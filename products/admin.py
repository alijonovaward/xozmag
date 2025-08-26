from django.contrib import admin
from .models import Product

class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Kelgan narxi'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return [
            ('0-10000', '0 - 10 000'),
            ('10000-50000', '10 000 - 50 000'),
            ('50000+', '50 000+'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == '0-10000':
            return queryset.filter(price__lt=10000)
        if value == '10000-50000':
            return queryset.filter(price__gte=10000, price__lt=50000)
        if value == '50000+':
            return queryset.filter(price__gte=50000)
        return queryset


class SellingPriceRangeFilter(admin.SimpleListFilter):
    title = 'Sotuv narxi'
    parameter_name = 'selling_price_range'

    def lookups(self, request, model_admin):
        return [
            ('0-10000', '0 - 10 000'),
            ('10000-50000', '10 000 - 50 000'),
            ('50000+', '50 000+'),
        ]

    def queryset(self, request, queryset):
        value = self.value()
        if value == '0-10000':
            return queryset.filter(selling_price__lt=10000)
        if value == '10000-50000':
            return queryset.filter(selling_price__gte=10000, selling_price__lt=50000)
        if value == '50000+':
            return queryset.filter(selling_price__gte=50000)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('profile', 'name', 'price', 'selling_price', 'stock', 'qrcode')
    list_filter = ('profile', PriceRangeFilter, SellingPriceRangeFilter)
    search_fields = ('name', 'qrcode')
