from django.views import View
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404, redirect, render
from product.models import Product


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'


