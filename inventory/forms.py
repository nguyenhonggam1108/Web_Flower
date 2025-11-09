from django import forms
from django.forms import inlineformset_factory
from .models import GoodsReceipt, GoodsReceiptItem

class GoodsReceiptForm(forms.ModelForm):
    class Meta:
        model = GoodsReceipt
        fields = ['supplier', 'invoice_file', 'note']

class GoodsReceiptItemForm(forms.ModelForm):
    class Meta:
        model = GoodsReceiptItem
        # không include content_type/object_id ở form, sẽ set trong view từ hidden inputs
        fields = ['quantity_bunch', 'unit_price']
        widgets = {
            'quantity_bunch': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

GoodsReceiptItemFormSet = inlineformset_factory(
    GoodsReceipt,
    GoodsReceiptItem,
    form=GoodsReceiptItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)