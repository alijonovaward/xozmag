from django.db import models

# Create your models here.
class Product(models.Model):
    profile = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=150, verbose_name='Nomi')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Kelgan narxi')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Sotuv narxi')
    stock = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Miqdori')
    qrcode = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name='QR Kod')  # Yangi maydon

    def __str__(self):
        return self.name[:50]