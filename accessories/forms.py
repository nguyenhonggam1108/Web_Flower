from django import forms
from .models import AccessoryItem

class AccessoryItemForm(forms.ModelForm):
    class Meta:
        model = AccessoryItem
        fields = ['category','name','price','stock','sku','description']