

# Register your models here.
from django.contrib import admin
from .models import Wishlist

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')  # nếu có trường created_at
    search_fields = ('user__username', 'product__name')