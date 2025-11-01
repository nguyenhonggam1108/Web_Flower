# cart/utils.py

from cart.models import CartItem
from product.models import Product

class CartMerger:
    def __init__(self, request):
        self.request = request
        self.session_cart = request.session.get('cart', {})

    def merge(self):
        if not self.session_cart or not self.request.user.is_authenticated:
            return

        for product_id, item in self.session_cart.items():
            product = Product.objects.filter(id=product_id).first()
            if not product:
                continue

            cart_item, created = CartItem.objects.get_or_create(
                user=self.request.user,
                product=product
            )
            cart_item.quantity += item['quantity']
            cart_item.save()

        del self.request.session['cart']