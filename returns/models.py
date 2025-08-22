from django.db import models
from products.models import Product
from django.contrib.auth.models import User

class ReturnedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} qaytarildi"
