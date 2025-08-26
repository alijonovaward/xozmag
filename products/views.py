from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Product
from django.db.models import Sum


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(profile=self.request.user.profile)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_products = self.get_queryset()
        context['total_products'] = user_products.count()
        context['total_price'] = user_products.aggregate(Sum('price'))['price__sum'] or 0
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
