from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect, render
from product.models import Product


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'


class ProductListView(ListView):
    model = Product                          # Model tương ứng
    template_name = 'product/product_list.html'  # Tên file template
    context_object_name = 'products'          # Tên biến trong template
    paginate_by = 12                          # ✅ Tùy chọn: phân trang 12 sản phẩm/trang