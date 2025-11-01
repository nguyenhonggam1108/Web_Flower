from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse

from .forms import RegisterForm, LoginForm
from .models import Customer


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'accounts/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']

            username = (first_name + last_name).lower().replace(" ", "")

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email đã được sử dụng.')
            elif Customer.objects.filter(phone=phone).exists():
                messages.error(request, 'Số điện thoại đã được sử dụng.')
            else:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=password
                )
                Customer.objects.create(user=user, phone=phone, address=address)
                messages.success(request, 'Đăng ký thành công!')
                return redirect(reverse('index'))
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(request, username=user_obj.username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, 'Đăng Nhập Thành Công!')
                    return redirect(reverse('index'))
                else:
                    form.add_error(None, 'Mật khẩu không đúng.')
            except User.DoesNotExist:
                form.add_error(None, 'Email không tồn tại.')
        return render(request, 'accounts/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Bạn đã đăng xuất thành công!')
        return redirect(reverse('index'))