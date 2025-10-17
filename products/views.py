from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Product
from django.db.models import Sum, F

from django.core.paginator import Paginator
from django.db.models import Q


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 30  # ✅ Har sahifada 30 ta mahsulot chiqadi

    def get_queryset(self):
        queryset = Product.objects.filter(profile=self.request.user.profile)
        search_query = self.request.GET.get('q', '').strip()

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(qrcode__icontains=search_query)
            )
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_products = self.get_queryset()

        context['total_products'] = user_products.count()

        # Jami tannarx: price * stock
        total_price = user_products.aggregate(
            total=Sum(F('price') * F('stock'))
        )['total'] or 0
        context['total_price'] = total_price

        # 🔍 Qidiruv qiymatini shablonda saqlab qolish uchun
        context['search_query'] = self.request.GET.get('q', '').strip()
        return context

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(profile=self.request.user.profile)


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'price', 'selling_price', 'stock', 'qrcode']  # qrcode qo'shildi
    template_name = 'products/product_form.html'

    def get_queryset(self):
        return Product.objects.filter(profile=self.request.user.profile)

    def get_success_url(self):
        return reverse_lazy('product-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        user_profile = self.request.user.profile
        name = form.cleaned_data['name']
        qrcode = form.cleaned_data.get('qrcode')

        # Mahsulot nomi takrorini tekshirish
        if Product.objects.filter(profile=user_profile, name__iexact=name).exclude(pk=self.object.pk).exists():
            form.add_error('name', 'Bu nomdagi mahsulot allaqachon mavjud!')
            return self.form_invalid(form)

        # QR kod takrorini tekshirish
        if qrcode and Product.objects.filter(profile=user_profile, qrcode=qrcode).exclude(pk=self.object.pk).exists():
            form.add_error('qrcode', 'Bu QR kod allaqachon ishlatilgan!')
            return self.form_invalid(form)

        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products')

    def get_queryset(self):
        return Product.objects.filter(profile=self.request.user.profile)


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'price', 'selling_price', 'stock', 'qrcode']  # qrcode qo'shildi
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products')

    def form_valid(self, form):
        user_profile = self.request.user.profile
        name = form.cleaned_data['name']
        qrcode = form.cleaned_data.get('qrcode')

        # Mahsulot nomi takrorini tekshirish
        if Product.objects.filter(profile=user_profile, name__iexact=name).exists():
            form.add_error('name', 'Bu nomdagi mahsulot allaqachon mavjud!')
            return self.form_invalid(form)

        # QR kod takrorini tekshirish
        if qrcode and Product.objects.filter(profile=user_profile, qrcode=qrcode).exists():
            form.add_error('qrcode', 'Bu QR kod allaqachon ishlatilgan!')
            return self.form_invalid(form)

        # Profilni bog‘lash
        form.instance.profile = user_profile
        return super().form_valid(form)

from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product


class AddStockView(LoginRequiredMixin, View):
    template_name = 'products/add_stock.html'

    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk, profile=request.user.profile)
        return render(request, self.template_name, {'product': product})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk, profile=request.user.profile)
        try:
            add_amount = Decimal(request.POST.get('amount', '0'))
            if add_amount <= 0:
                messages.error(request, "Miqdor musbat bo‘lishi kerak.")
            else:
                product.stock += add_amount
                product.save()
                messages.success(request, f"{product.name} mahsulotiga {add_amount} birlik qo‘shildi.")
                return redirect('products')
        except Exception:
            messages.error(request, "Noto‘g‘ri qiymat kiritildi.")
        return render(request, self.template_name, {'product': product})
