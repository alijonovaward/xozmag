from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from sale.models import Receipt, ReceiptItem
from products.models import Product


@login_required
def dashboard(request):
    user = request.user

    # Sana bo‘yicha filter
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Foydalanuvchiga tegishli barcha receipts
    all_receipts = (
        Receipt.objects.filter(user=user)
        .prefetch_related('items')  # oldindan ReceiptItem larni olib keladi
        .order_by('-created_at')
    )

    # Filterlangan receipts
    filtered_receipts = all_receipts
    if start_date:
        filtered_receipts = filtered_receipts.filter(created_at__date__gte=start_date)
    if end_date:
        filtered_receipts = filtered_receipts.filter(created_at__date__lte=end_date)

    # Bugungi receipts
    today = timezone.localdate()
    today_receipts = all_receipts.filter(created_at__date=today)

    # --- OPTIMALLASH UCHUN: Barcha productlarni oldindan olish ---
    # Bitta query bilan barcha productlar (name -> obj)
    products_map = {
        p.name: p for p in Product.objects.filter(profile=user.profile).only('name', 'price', 'selling_price')
    }

    # Aggregatsiya funksiyasi
    def aggregate_receipts(qs):
        product_stats = {}
        total_sum = 0
        total_profit = 0

        # faqat kerakli receipt_item larni oldindan olish
        receipt_items = ReceiptItem.objects.filter(receipt__in=qs).select_related(None)

        for item in receipt_items:
            product = products_map.get(item.product_name)
            selling_price = float(product.selling_price) if product else float(item.price)
            cost_price = float(getattr(product, 'price', 0)) if product else 0.0

            item_total = selling_price * float(item.quantity)
            profit = (selling_price - cost_price) * float(item.quantity)

            total_sum += item_total
            total_profit += profit

            stats = product_stats.setdefault(item.product_name, {
                'quantity': 0,
                'total_sales': 0,
                'total_profit': 0
            })
            stats['quantity'] += float(item.quantity)
            stats['total_sales'] += item_total
            stats['total_profit'] += profit

        # Dict → List
        product_list = [
            {
                'product_name': name,
                'quantity': stats['quantity'],
                'total_sales': stats['total_sales'],
                'total_profit': stats['total_profit']
            }
            for name, stats in product_stats.items()
        ]

        return product_list, total_sum, total_profit

    # Bugungi va filterlangan aggregate
    today_products, today_total, today_profit = aggregate_receipts(today_receipts)
    filtered_products, filtered_total, filtered_profit = aggregate_receipts(filtered_receipts)

    context = {
        'today_products': today_products,
        'today_total': today_total,
        'today_profit': today_profit,
        'filtered_products': filtered_products,
        'filtered_total': filtered_total,
        'filtered_profit': filtered_profit,
        'start_date': start_date or '',
        'end_date': end_date or '',
    }
    return render(request, 'stats/dashboard.html', context)
