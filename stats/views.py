from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime
from sale.models import Receipt, ReceiptItem
from products.models import Product  # Product import

@login_required
def dashboard(request):
    user = request.user

    # Vaqt bo‘yicha filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    receipts = Receipt.objects.filter(user=user).prefetch_related('items').order_by('-created_at')

    if start_date:
        receipts = receipts.filter(created_at__date__gte=start_date)
    if end_date:
        receipts = receipts.filter(created_at__date__lte=end_date)

    # Bugungi cheklar
    today = timezone.localdate()
    today_receipts = receipts.filter(created_at__date=today)

    # Jami summalarni hisoblash
    def get_receipt_items_with_prices(qs):
        items_list = []
        total_sum = 0
        total_plus = 0
        for r in qs:
            for item in r.items.all():
                try:
                    product = Product.objects.get(name=item.product_name, profile=user.profile)
                    selling_price = float(product.selling_price)
                    cost_price = float(getattr(product, 'price', 0))  # agar cost price kerak bo‘lsa
                except Product.DoesNotExist:
                    selling_price = float(item.price)
                    cost_price = 0
                item_total = selling_price * float(item.quantity)
                total_sum += item_total
                plus = (selling_price - cost_price) * float(item.quantity)
                total_plus += plus
                items_list.append({
                    'receipt_id': r.id,
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'selling_price': selling_price,
                    'cost_price': cost_price,
                    'item_total': item_total,
                    'description': r.description,
                    'created_at': r.created_at,
                    'plus':plus
                })
        return items_list, total_sum, total_plus

    today_items, today_total, today_plus = get_receipt_items_with_prices(today_receipts)
    filtered_items, filtered_total, total_plus = get_receipt_items_with_prices(receipts)

    context = {
        'today_items': today_items,
        'today_total': today_total,
        'today_plus': today_plus,
        'filtered_items': filtered_items,
        'filtered_total': filtered_total,
        'total_plus': total_plus,
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'stats/dashboard.html', context)
