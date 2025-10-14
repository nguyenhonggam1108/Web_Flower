from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from category.models import Category
from django.views.generic import TemplateView , ListView

from product.models import Product

from accounts.models import Customer


# Create your views here.

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.all()
        return context


class AboutView(TemplateView):
    template_name = "about.html"

class SaleView(TemplateView):
    template_name = "sale.html"

class DesignView(TemplateView):
    template_name = "design.html"

class ThemedView(TemplateView):
    template_name = "themed.html"


# ----DropDown----
class AllFlowerView(ListView):
    model = Product
    template_name = "dropdown/all_flower.html"
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = {'name': 'Tất cả sản phẩm'}
        return context


class BoHoaTuoiView(TemplateView):
    template_name = "dropdown/bo_hoa_tuoi.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = Category.objects.get(name__iexact="bo_hoa_tuoi")
            products = Product.objects.filter(category=category)
        except Category.DoesNotExist:
            category = {'name': 'Bó Hoa Tươi'}
            products = []
        context['products'] = products
        context['category'] = category
        return context




class ChauHoaView(TemplateView):
    template_name = "dropdown/chau_hoa.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = Category.objects.get(name__iexact="Chau Hoa")
            products = Product.objects.filter(category=category)
        except Category.DoesNotExist:
            category = {'name': 'Chậu Hoa'}
            products = []
        context['products'] = products
        context['category'] = category
        return context



class HoaSapView(TemplateView):
    template_name = "dropdown/hoa_sap.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = Category.objects.get(name__iexact="Hoa Sáp")
            products = Product.objects.filter(category=category)
        except Category.DoesNotExist:
            category = {'name': 'Hoa Sáp'}
            products = []
        context['products'] = products
        context['category'] = category
        return context


# ----DropDown_Themed----
class HoaChiaBuonView(TemplateView):
    template_name = "dropdown/themed_flower/hoa_chia_buon.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = Category.objects.get(name__iexact="Hoa Chia Buồn")
            products = Product.objects.filter(category=category)
        except Category.DoesNotExist:
            category = {'name': 'Hoa Chia Buồn'}
            products = []
        context['products'] = products
        context['category'] = category
        return context


class HoaChucMungView(TemplateView):
    template_name = "dropdown/themed_flower/hoa_chuc_mung.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = Category.objects.get(name__iexact="Hoa Chúc Mừng ")
            products = Product.objects.filter(category=category)
        except Category.DoesNotExist:
            category = {'name': 'Hoa Chúc Mừng'}
            products = []
        context['products'] = products
        context['category'] = category
        return context

class HoaCuoiView(TemplateView):
    template_name = "dropdown/themed_flower/hoa_cuoi.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = Category.objects.get(name__iexact="Hoa Cưới ")
            products = Product.objects.filter(category=category)
        except Category.DoesNotExist:
            category = {'name': 'Hoa Cưới'}
            products = []
        context['products'] = products
        context['category'] = category
        return context

class HoaSinhNhatView(TemplateView):
    template_name = "dropdown/themed_flower/hoa_sinh_nhat.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = Category.objects.get(name__iexact="Hoa Sinh Nhật ")
            products = Product.objects.filter(category=category)
        except Category.DoesNotExist:
            category = {'name': 'Hoa Sinh Nhật'}
            products = []
        context['products'] = products
        context['category'] = category
        return context

class HoaTinhYeuView(TemplateView):
    template_name = "dropdown/themed_flower/hoa_tinh_yeu.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            category = Category.objects.get(name__iexact="Hoa Tình Yêu ")
            products = Product.objects.filter(category=category)
        except Category.DoesNotExist:
            category = {'name': 'Hoa Tình Yêu'}
            products = []
        context['products'] = products
        context['category'] = category
        return context

