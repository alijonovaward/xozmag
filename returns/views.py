from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
from .forms import ReturnedProductForm
from .models import ReturnedProduct
from products.models import Product
from sale.models import Receipt, ReceiptItem   # receipt modelingiz qaerda bo'lsa o'shani import qiling


def return_product_page(request):
    if request.method == 'POST':
        form = ReturnedProductForm(request.POST, user=request.user)
        if form.is_valid():
            returned = form.save(commit=False)
            returned.user = request.user
            product = returned.product

            # Omborga qaytarish (stock ni oshirish)
            product.stock += returned.quantity
            product.save()

            # Qaytarilgan tovarni saqlash
            returned.save()

            # Qaytarish uchun yangi Receipt ochamiz (minus yozuv bilan)
            receipt = Receipt.objects.create(
                user=request.user,
                description=f"Qaytarish: {product.name}",
                ready=True
            )
            ReceiptItem.objects.create(
                receipt=receipt,
                product_name=product.name,
                price=product.selling_price,
                quantity=-returned.quantity   # MINUS yozuv!
            )

            return redirect('returned_list')  # qaytarilganlar sahifasiga o'tish
    else:
        form = ReturnedProductForm(user=request.user)

    return render(request, 'returns/return_page.html', {'form': form})


def returned_list(request):
    # Asosiy queryset
    returns = ReturnedProduct.objects.filter(user=request.user).select_related('product').order_by('-date')

    # GET so'rovdan filter sanalarini olish
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        start_date = parse_date(start_date)
        if start_date:
            returns = returns.filter(date__date__gte=start_date)

    if end_date:
        end_date = parse_date(end_date)
        if end_date:
            returns = returns.filter(date__date__lte=end_date)

    context = {
        'returns': returns,
        'start_date': request.GET.get('start_date', ''),
        'end_date': request.GET.get('end_date', '')
    }
    return render(request, 'returns/returned_list.html', context)
