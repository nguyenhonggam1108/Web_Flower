from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render

# Create your views here.
# cart/views.py
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from product.models import Product
from django.http import JsonResponse

class CartView(View):
    def get(self, request):
        cart = request.session.get('cart', {})
        total = sum(item['price'] * item['quantity'] for item in cart.values())
        return render(request, 'cart/cart_view.html', {'cart': cart, 'total': total})


class AddToCartView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'  # ✅ đường dẫn khi chưa đăng nhập
    redirect_field_name = None      # ✅ để tránh Django thêm ?next=... vào URL

    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            cart[str(product_id)]['quantity'] += quantity
        else:
            cart[str(product_id)] = {
                'name': product.name,
                'price': float(product.price),
                'quantity': quantity,
            }

        request.session['cart'] = cart

        return JsonResponse({
            'success': True,
            'message': f'Đã thêm {product.name} vào giỏ hàng!',
            'cart_count': len(cart)
        })

class UpdateCartView(View):
    def post(self, request, product_id):
        cart = request.session.get('cart', {})
        quantity = int(request.POST.get('quantity', 1))
        if str(product_id) in cart:
            if quantity > 0:
                cart[str(product_id)]['quantity'] = quantity
            else:
                del cart[str(product_id)]
        request.session['cart'] = cart
        return redirect('cart:view_cart')


class RemoveFromCartView(View):
    def post(self, request, product_id):
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            del cart[str(product_id)]
        request.session['cart'] = cart
        return redirect('cart:view_cart')
