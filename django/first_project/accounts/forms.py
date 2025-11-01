from django import forms
from django.contrib.auth.models import User
from .models import Customer

class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, label='Họ')
    last_name = forms.CharField(max_length=30, label='Tên')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu')
    address = forms.CharField(required=True)

    class Meta:
        model = Customer
        fields = ['phone']

class LoginForm(forms.Form):
    email = forms.CharField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Mật khẩu')
