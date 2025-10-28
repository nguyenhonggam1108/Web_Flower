from django.urls import path
from . import views
from .views import CategoryDetailView, AllProductsView

urlpatterns = [
    path('<int:cat_id>/',CategoryDetailView.as_view(), name='category_detail'),
    path('all/', AllProductsView.as_view(), name='all_products'),
]