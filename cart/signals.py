# cart/signals.py

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from cart.utils import CartMerger  # hoặc hàm merge_session_cart_to_user

@receiver(user_logged_in)
def sync_cart_after_login(sender, request, user, **kwargs):
    CartMerger(request).merge()