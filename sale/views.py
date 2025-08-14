from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Receipt, ReceiptItem

@login_required
def sales_page(request):
    """
    Boshlang'ich sahifani chizamiz. Sessiondagi 'cart' JSON-serializable bo'lishi kerak
    (faqat str/float/int/bool/list/dict). Shuning uchun float saqlaymiz.
    """
    cart = request.session.get('cart', {})
    # Boshlang'ich render uchun jami hisoblab beramiz (template’da ko‘rsatish uchun)
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
    return render(request, 'sale/sales.html', {'cart': cart, 'rows': rows})

@login_required
def product_search_api(request):
    q = request.GET.get('q', '').strip()
    profile = request.user.profile

    # Agar input bo'sh bo'lsa, hech narsa qaytarmaymiz
    if not q:
        return JsonResponse({'results': []})

    products = Product.objects.filter(profile=profile, name__icontains=q)[:10]
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


@login_required
@require_POST
def add_to_cart(request, product_id):
    """
    Quantity ni foydalanuvchi nuqta yoki vergul bilan kiritsa ham qabul qilamiz.
    Sessiyaga faqat float saqlaymiz (Decimal yo'q) — aks holda JSON serialize xatosi bo'ladi.
    """
    product = get_object_or_404(Product, id=product_id)

    raw_qty = (request.POST.get('quantity') or '1').strip()
    # Vergulni nuqtaga almashtiramiz
    raw_qty = raw_qty.replace(',', '.')
    try:
        quantity = Decimal(raw_qty)
    except (InvalidOperation, TypeError):
        return JsonResponse({'success': False, 'error': 'Noto‘g‘ri miqdor'}, status=400)

    if quantity <= 0:
        return JsonResponse({'success': False, 'error': 'Miqdor > 0 bo‘lishi kerak'}, status=400)

    cart = request.session.get('cart', {})
    pid = str(product.id)

    # Sessiyada faqat float saqlaymiz
    if pid in cart:
        cart[pid]['quantity'] = float(cart[pid]['quantity']) + float(quantity)
    else:
        cart[pid] = {
            'name': product.name,
            'price': float(product.selling_price),
            'quantity': float(quantity),
        }

    request.session['cart'] = cart
    return JsonResponse({'success': True, 'cart': cart})

@login_required
@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session['cart'] = cart
        return JsonResponse({'success': True, 'cart': cart})
    return JsonResponse({'success': False, 'error': 'Mahsulot topilmadi'}, status=404)

@login_required
def close_cart(request):
    """
    Chek yaratamiz, stockni kamaytiramiz. Bu yerda Decimal bilan ishlaymiz,
    lekin sessiyadan o‘qiganimiz float — shuni Decimal ga aylantirib olamiz.
    """
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('sales_page')

    receipt = Receipt.objects.create(user=request.user)
    for pid, item in cart.items():
        product = Product.objects.get(id=int(pid))
        qty = Decimal(str(item['quantity']))
        price = Decimal(str(item['price']))

        # Stokni kamaytirish
        product.stock -= qty
        product.save()

        # Chek item
        ReceiptItem.objects.create(
            receipt=receipt,
            product_name=item['name'],
            price=price,
            quantity=qty,
        )

    # Sessiyani tozalaymiz
    request.session['cart'] = {}
    return redirect('sales_page')
