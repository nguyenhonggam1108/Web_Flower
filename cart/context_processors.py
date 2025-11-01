# cart/context_processors.py

from cart.models import CartItem
from django.db.models import Sum

def cart_total_quantity(request):
    if request.user.is_authenticated:
        total_quantity = CartItem.objects.filter(user=request.user).aggregate(
            Sum('quantity')
        )['quantity__sum'] or 0
    else:
        cart = request.session.get('cart', {})
        total_quantity = sum(item['quantity'] for item in cart.values())
    print("Session cart:", request.session.get('cart'))
    return {'cart_total_quantity': total_quantity}
