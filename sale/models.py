from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ready = models.BooleanField(default=False)

    def __str__(self):
        return f"Receipt #{self.id} - {self.user.username}"

    def get_total(self):
        return sum(item.price * item.quantity for item in self.items.all())

class ReceiptItem(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
