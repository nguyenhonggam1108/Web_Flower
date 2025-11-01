from django.urls import path
from . import views
from .views import CartView, AddToCartView, UpdateCartView, RemoveFromCartView

app_name = 'cart'

urlpatterns = [
    path('',CartView.as_view(), name='view_cart'),
    path('add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('update/<int:item_id>/', UpdateCartView.as_view(), name='update_cart'),
    path('remove/<int:item_id>/', RemoveFromCartView.as_view(), name='remove_from_cart'),
]
