from django.db import models
from django.contrib.auth.models import User
from product.models import Product

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity} ({self.user.username})"

    def get_total_price(self):
        return self.product.price * self.quantity

class CartSyncService:
    def __init__(self, request):
        self.request = request
        self.session_cart = request.session.get('cart', {})

    def sync_to_db(self):
        if self.request.user.is_authenticated and self.session_cart:
            for product_id, item in self.session_cart.items():
                product = Product.objects.get(id=product_id)
                cart_item, created = CartItem.objects.get_or_create(
                    user=self.request.user,
                    product=product,
                    defaults={'quantity': item['quantity']}
                )
                if not created:
                    cart_item.quantity += item['quantity']
                    cart_item.save()
            del self.request.session['cart']
