from django import forms

from shop.models import Order


class OrderForm(forms.ModelForm):

    class Meta:
        model = Order
        exclude = ('purchase',)
        widgets = {
            'payment_method': forms.RadioSelect(),
            'address': forms.Textarea()
        }
