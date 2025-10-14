from django.shortcuts import render, get_object_or_404

from category.models import Category
from django.views.generic import TemplateView

from product.models import Product


# Create your views here.
class CategoryDetailView(TemplateView):
    template_name = 'category/category_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cat_id = self.kwargs.get('cat_id')
        category = get_object_or_404(Category, id=cat_id)
        products = Product.objects.filter(category=category)
        context['category'] = category
        context['products'] = products
        return context


class AllProductsView(TemplateView):
    template_name = 'category/category_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context
