from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from products.models import Product
from .models import Receipt, ReceiptItem
from accounts.models import Profile


# ==============================
# Foydalanuvchi aktiv cartni olish
# ==============================
def get_active_cart_key(request):
    active_key = request.session.get("active_cart", "cart1")
    if active_key not in ["cart1", "cart2", "cart3"]:
        active_key = "cart1"
    return active_key


# ==============================
# Savdo sahifasi
# ==============================
@login_required
def sales_page(request):
    active_key = get_active_cart_key(request)
    cart = request.session.get(active_key, {})
    rows = []
    for pid, item in cart.items():
        price = float(item['price'])
        qty = float(item['quantity'])
        rows.append({
            'id': pid,
            'name': item['name'],
            'price': price,
            'quantity': qty,
            'total': round(price * qty, 2),
        })
    return render(request, 'sale/sales.html', {'cart': cart, 'rows': rows, 'active_cart': active_key})


# ==============================
# Mahsulot qidiruv API
# ==============================
@login_required
def product_search_api(request):
    q = request.GET.get('q', '').strip()
    profile = request.user.profile
    if not q:
        return JsonResponse({'results': []})

    products = Product.objects.filter(
        profile=profile
    ).filter(
        Q(name__icontains=q) | Q(qrcode=q)
    )[:10]

    data = [
        {
            'id': p.id,
            'name': p.name,
            'selling_price': str(p.selling_price),
            'stock': str(p.stock),
        }
        for p in products
    ]
    return JsonResponse({'results': data})


# ==============================
# Korzinkaga mahsulot qo'shish
# ==============================
@login_required
@require_POST
def add_to_cart(request, product_id):
    active_key = get_active_cart_key(request)
    product = get_object_or_404(Product, id=product_id)
    raw_qty = (request.POST.get('quantity') or '1').strip()
    raw_qty = raw_qty.replace(',', '.')
    try:
        quantity = Decimal(raw_qty)
    except (InvalidOperation, TypeError):
        return JsonResponse({'success': False, 'error': 'Noto‘g‘ri miqdor'}, status=400)
    if quantity <= 0:
        return JsonResponse({'success': False, 'error': 'Miqdor > 0 bo‘lishi kerak'}, status=400)

    cart = request.session.get(active_key, {})
    pid = str(product.id)
    if pid in cart:
        cart[pid]['quantity'] = float(cart[pid]['quantity']) + float(quantity)
    else:
        cart[pid] = {
            'name': product.name,
            'price': float(product.selling_price),
            'quantity': float(quantity),
        }
    request.session[active_key] = cart
    return JsonResponse({'success': True, 'cart': cart})


# ==============================
# Korzinkadan mahsulot o'chirish
# ==============================
@login_required
@require_POST
def remove_from_cart(request, product_id):
    active_key = get_active_cart_key(request)
    cart = request.session.get(active_key, {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session[active_key] = cart
        return JsonResponse({'success': True, 'cart': cart})
    return JsonResponse({'success': False, 'error': 'Mahsulot topilmadi'}, status=404)


# ==============================
# Korzinkani yopish va chek yaratish
# ==============================
@login_required
@require_POST
def close_cart(request):
    active_key = get_active_cart_key(request)
    cart = request.session.get(active_key, {})
    if not cart:
        return JsonResponse({'success': False, 'error': 'Korzinka bo‘sh'})

    description = request.POST.get('description', '').strip()
    receipt = Receipt.objects.create(user=request.user, description=description)
    items_data = []
    total = Decimal('0.00')

    for pid, item in cart.items():
        product = Product.objects.get(id=int(pid))
        qty = Decimal(str(item['quantity']))
        price = Decimal(str(item['price']))
        product.stock -= qty
        product.save()

        ReceiptItem.objects.create(
            receipt=receipt,
            product_name=item['name'],
            price=price,
            quantity=qty,
        )
        total += price * qty
        items_data.append({
            'name': item['name'],
            'price': str(price),
            'quantity': str(qty),
            'total': str(price * qty)
        })

    request.session[active_key] = {}

    profile = Profile.objects.filter(user=request.user).first()
    profile_name = profile.name if profile and profile.name else "Do‘kon nomi belgilanmagan"
    profile_location = profile.location if profile and profile.location else "Manzil belgilanmagan"
    return JsonResponse({'success': True, 'items': items_data, 'total': str(total), 'name':profile_name, 'location':profile_location})


# ==============================
# Cheklar ro'yxati
# ==============================
from django.core.paginator import Paginator


@login_required
def receipt_list(request):
    receipts = (
        Receipt.objects
        .filter(user=request.user)
        .prefetch_related('items')
        .order_by('-created_at')
    )

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    description = request.GET.get('description')
    ready_filter = request.GET.get('ready')

    if start_date:
        receipts = receipts.filter(created_at__date__gte=start_date)
    if end_date:
        receipts = receipts.filter(created_at__date__lte=end_date)
    if description:
        receipts = receipts.filter(description__icontains=description)
    if ready_filter in ['true', 'false']:
        receipts = receipts.filter(ready=(ready_filter == 'true'))

    page_number = request.GET.get('page', 1)
    paginator = Paginator(receipts, 20)
    page_obj = paginator.get_page(page_number)

    profile = Profile.objects.filter(user=request.user).first()
    profile_name = profile.name if profile and profile.name else "Do‘kon nomi belgilanmagan"
    profile_location = profile.location if profile and profile.location else "Manzil belgilanmagan"

    context = {
        'receipts': page_obj,
        'start_date': start_date or '',
        'end_date': end_date or '',
        'description': description or '',
        'ready_filter': ready_filter or '',
        'paginator': paginator,
        'page_obj': page_obj,
        'name': profile_name,
        'location': profile_location
    }
    return render(request, 'sale/receipts.html', context)


@login_required
@require_POST
def toggle_ready(request, receipt_id):
    receipt = get_object_or_404(Receipt, id=receipt_id, user=request.user)
    receipt.ready = not receipt.ready
    receipt.save()
    return JsonResponse({'success': True, 'ready': receipt.ready})


# ==============================
# Aktiv korzinkani almashtirish
# ==============================
@login_required
def set_active_cart(request, cart_number):
    """cart_number: 1, 2 yoki 3"""
    if cart_number not in ['1', '2', '3']:
        return JsonResponse({'success': False, 'error': 'Noto‘g‘ri cart raqami'})
    request.session['active_cart'] = f'cart{cart_number}'
    return JsonResponse({'success': True, 'active_cart': request.session['active_cart']})
