from django.urls import path
from . import views

app_name = 'accessories'

urlpatterns = [
    path('', views.AccessoryListView.as_view(), name='list'),
    path('<slug:slug>/', views.AccessoryDetailView.as_view(), name='detail'),
    # optional API for frontend
    path('api/categories/', views.AccessoryCategoryListAPI.as_view(), name='api_categories'),
    path('api/items-by-category/<int:category_id>/', views.AccessoryItemsByCategoryAPI.as_view(), name='api_items_by_category'),
]