from django import forms
from .models import Order, DeliveryProof

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'is_paid']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_paid': forms.CheckboxInput(),
        }

class DeliveryProofForm(forms.ModelForm):
    class Meta:
        model = DeliveryProof
        fields = ['image', 'note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }