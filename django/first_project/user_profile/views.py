from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from accounts.models import Customer
from .forms import CustomerForm, UserForm


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        return render(request, "user_profile/profile.html", {'customer': customer})



class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        customer = Customer.objects.get(user=request.user)
        user_form = UserForm(instance=request.user)
        customer_form = CustomerForm(instance=customer)
        return render(request, 'edit/edit_profile.html', {
            'user_form': user_form,
            'form': customer_form
        })

    def post(self, request):
        customer = Customer.objects.get(user=request.user)
        user_form = UserForm(request.POST, instance=request.user)
        customer_form = CustomerForm(request.POST, instance=customer)

        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            customer_form.save()
            return redirect('user_profile:profile_view')

        return render(request, 'edit/edit_profile.html', {
            'user_form': user_form,
            'form': customer_form
        })