from django.urls import path
from . import views
from .views import ProductDetailView, ProductListView

urlpatterns = [
    path('', ProductListView.as_view(), name='product_list'),
    path('<int:product_id>/',ProductDetailView.as_view(), name='product_detail'),
]
