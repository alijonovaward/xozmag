from django.contrib import admin
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from .models import Receipt, ReceiptItem


class ReceiptItemInline(admin.TabularInline):
    model = ReceiptItem
    extra = 0
    fields = ("product_name", "price", "quantity", "line_total")
    readonly_fields = ("line_total",)
    can_delete = True
    show_change_link = True

    def line_total(self, obj):
        # Yangi qator (hanuz saqlanmagan) uchun bo'sh qoldiramiz
        if obj.pk is None:
            return ""
        return obj.price * obj.quantity
    line_total.short_description = "Jami"


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    # Jadval ustunlari
    list_display = ("id", "user", "created_at", "ready", "total_amount_display")
    list_display_links = ("id", "user")
    list_editable = ("ready",)

    # Filtrlar va qidiruv
    list_filter = ("ready", "user", ("created_at", admin.DateFieldListFilter))
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "description",
        "items__product_name",
    )

    # Chiroyli navigatsiya
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 50

    # Form xususiyatlari
    readonly_fields = ("created_at", "total_amount_display")
    autocomplete_fields = ("user",)
    inlines = [ReceiptItemInline]
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = True
    list_select_related = ("user",)

    # Annotatsiya: umumiy summani bazada hisoblab keltiramiz
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        total_expr = ExpressionWrapper(
            F("items__price") * F("items__quantity"),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        )
        return qs.annotate(total_amount=Sum(total_expr))

    @admin.display(ordering="total_amount", description="Umumiy summa")
    def total_amount_display(self, obj):
        from decimal import Decimal
        return obj.total_amount if obj.total_amount is not None else Decimal("0.00")

    # Qidiruvda dublikatlarni oldini olish (reverse FK bo‘lgani uchun)
    def get_search_results(self, request, queryset, search_term):
        qs, use_distinct = super().get_search_results(request, queryset, search_term)
        return qs.distinct(), True

    # Fieldsetlar: Asosiy va Tizim bo‘limlari
    fieldsets = (
        ("Asosiy ma'lumotlar", {"fields": ("user", "description", "ready")}),
        (
            "Tizim (o'qish uchun)",
            {"fields": ("created_at", "total_amount_display"), "classes": ("collapse",)},
        ),
    )

    # ACTIONS
    @admin.action(description="Tanlangan receiptlarni Ready qilish")
    def mark_ready(self, request, queryset):
        updated = queryset.update(ready=True)
        self.message_user(request, f"{updated} ta receipt 'ready' qilindi.")

    @admin.action(description="Tanlangan receiptlarni Ready emas qilish")
    def mark_not_ready(self, request, queryset):
        updated = queryset.update(ready=False)
        self.message_user(request, f"{updated} ta receipt 'ready' bekor qilindi.")

    @admin.action(description="Tanlangan receiptlarni CSV qilib yuklab olish")
    def export_as_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=receipts.csv"
        writer = csv.writer(response)
        writer.writerow(["ID", "User", "Created at", "Ready", "Total", "Description"])

        for r in queryset:
            total = getattr(r, "total_amount", None)
            if total is None:
                total = r.get_total()
            writer.writerow(
                [r.id, r.user.username, r.created_at, r.ready, total, r.description or ""]
            )
        return response

    actions = ("mark_ready", "mark_not_ready", "export_as_csv")


@admin.register(ReceiptItem)
class ReceiptItemAdmin(admin.ModelAdmin):
    list_display = ("id", "receipt", "product_name", "price", "quantity", "line_total")
    list_filter = (("receipt__created_at", admin.DateFieldListFilter), "receipt__user", "receipt__ready")
    search_fields = ("product_name", "receipt__user__username", "receipt__description")
    readonly_fields = ("line_total",)
    raw_id_fields = ("receipt",)
    list_select_related = ("receipt", "receipt__user")
    ordering = ("-id",)
    list_per_page = 100
    save_on_top = True

    @admin.display(description="Jami")
    def line_total(self, obj):
        return obj.price * obj.quantity
