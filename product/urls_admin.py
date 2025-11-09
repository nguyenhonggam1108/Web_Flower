from django.urls import path

from product.view_admin import ProductListView, ProductCreateView, ProductDetailView, \
    ProductUpdateView, ProductDeleteView

app_name = 'product_admin'

urlpatterns = [
    path('', ProductListView.as_view(), name='list'),
    path('add/', ProductCreateView.as_view(), name='add'),
    path('<int:pk>/', ProductDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', ProductUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='delete'),
]
