from django.views import View
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404, redirect, render
from product.models import Product


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    pk_url_kwarg = 'product_id'


class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += quantity
        else:
            cart[str(product_id)] = {
                'name': product.name,
                'price': product.price,
                'quantity': quantity,
            }

        request.session['cart'] = cart
        return redirect('cart')