from django import forms
from .models import ReturnedProduct
from products.models import Product

class ReturnedProductForm(forms.ModelForm):
    product = forms.ModelChoiceField(queryset=Product.objects.none(), label="Tovar")

    class Meta:
        model = ReturnedProduct
        fields = ['product', 'quantity', 'reason']
        labels = {
            'quantity': 'Miqdor',
            'reason': 'Sabab (ixtiyoriy)',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        # faqat user profiliga tegishli productlar
        self.fields['product'].queryset = Product.objects.filter(profile__user=user)
