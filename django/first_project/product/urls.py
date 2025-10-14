from django.urls import path
from . import views
from .views import ProductDetailView, AddToCartView

urlpatterns = [
    # path('', views.product_detail, name='product_detail'),
    path('<int:product_id>/',ProductDetailView.as_view(), name='product_detail'),
    path('<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
]
