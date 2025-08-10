from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Product

class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(profile=self.request.user.profile)

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(profile=self.request.user.profile)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'price', 'selling_price', 'stock']
    template_name = 'products/product_form.html'

    def get_queryset(self):
        return Product.objects.filter(profile=self.request.user.profile)

    def get_success_url(self):
        return reverse_lazy('product-detail', kwargs={'pk': self.object.pk})

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('products')

    def get_queryset(self):
        return Product.objects.filter(profile=self.request.user.profile)

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'price', 'selling_price', 'stock']
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('products')

    def form_valid(self, form):
        # Saqlashdan oldin productga hozirgi user profilini bog'laymiz
        form.instance.profile = self.request.user.profile
        return super().form_valid(form)