from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from accounts.models import Customer
from .forms import CustomerForm


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        return render(request, "user_profile/profile.html", {'customer': customer})


class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        form = CustomerForm(instance=customer)
        return render(request, 'edit/edit_profile.html', {'form': form})

    def post(self, request):
        customer = Customer.objects.get(user=request.user)
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('profile_view')  # tên này phải khớp với name trong urls.py
        return render(request, 'edit/edit_profile.html', {'form': form})