from django.urls import path
from .views import ToggleWishlistView, GetWishlistView, WishlistStatusView, WishlistPageView, RemoveFromWishlistView

app_name= 'wishlist'

urlpatterns = [
    path('wishlist_page/', WishlistPageView.as_view(), name='wishlist_page'),
    path('toggle/', ToggleWishlistView.as_view(), name='toggle_wishlist'),
    path('get/', GetWishlistView.as_view(), name='get_wishlist'),
    path('status/<int:product_id>/', WishlistStatusView.as_view(), name='wishlista_status'),
    path('remove/<int:product_id>/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
]
