from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Product
from category.models import Category
from django.db.models import Q

class ProductAdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = '/accounts/login/'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class ProductListView(ProductAdminRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '')
        category_id = request.GET.get('category', '')

        products = Product.objects.all()

        if query:
            products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
        if category_id:
            products = products.filter(category_id=category_id)

        categories = Category.objects.all()

        context = {
            'products': products,
            'categories': categories,
            'selected_category': category_id,
            'query': query,
        }
        return render(request, 'product/product_admin_list.html', context)

# ➕ Thêm sản phẩm
class ProductCreateView(ProductAdminRequiredMixin, View):
    def get(self, request):
        categories = Category.objects.all()
        return render(request, 'product/product_form.html', {'categories': categories})

    def post(self, request):
        name = request.POST.get('name')
        price = request.POST.get('price')
        description = request.POST.get('description')
        category_id = request.POST.get('category')
        status = request.POST.get('status')
        image = request.FILES.get('image')

        Product.objects.create(
            name=name,
            price=price,
            description=description,
            category_id=category_id,
            status=status,
            image=image
        )
        messages.success(request, "✅ Đã thêm sản phẩm thành công!")
        return redirect(reverse('product_admin:list'))


# ✏ Sửa sản phẩm
class ProductUpdateView(ProductAdminRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        categories = Category.objects.all()
        return render(request, 'product/product_form.html', {'product': product, 'categories': categories})

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        product.category_id = request.POST.get('category')
        product.status = request.POST.get('status')

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        messages.success(request, "✏ Cập nhật sản phẩm thành công!")
        return redirect(reverse('product_admin:list'))


# 👁 Xem chi tiết sản phẩm
class ProductDetailView(ProductAdminRequiredMixin, View):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'product/product_detail_admin.html', {'product': product})


# ❌ Xóa sản phẩm
class ProductDeleteView(ProductAdminRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        messages.warning(request, "🗑 Đã xóa sản phẩm.")
        return redirect(reverse('product_admin:list'))