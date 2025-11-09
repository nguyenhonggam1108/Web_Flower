from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.InventoryListView.as_view(), name='list'),
    path('add/', views.InventoryCreateView.as_view(), name='add'),
    path('import/', views.InventoryCreateView.as_view(), name='import'),
    path('report/', views.InventoryReportView.as_view(), name='report'),
    path('receipts/', views.GoodsReceiptListView.as_view(), name='receipts_list'),
    path('receipts/add/', views.GoodsReceiptCreateView.as_view(), name='receipts_add'),
    path('receipts/<int:receipt_id>/', views.GoodsReceiptDetailView.as_view(), name='receipts_detail'),

    # Category manager
    path('manage-categories/', views.CategoryManagerView.as_view(), name='manage_categories'),
    path('manage-categories/add/', views.CategoryCreateView.as_view(), name='category_add'),
    path('manage-categories/<str:app_label>/<str:model_name>/edit/<int:pk>/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('manage-categories/<str:app_label>/<str:model_name>/delete/<int:pk>/', views.CategoryDeleteView.as_view(), name='category_delete'),

    path('api/categories/', views.FlowerCategoryListAPI.as_view(), name='api_categories'),
    path('api/flowers-by-category/<int:category_id>/', views.FlowersByCategoryAPI.as_view(), name='api_flowers_by_category'),

    path('api/items-by-category/<str:app_label>/<int:category_id>/', views.ItemsByCategoryAPI.as_view(), name='api_items_by_category'),
]