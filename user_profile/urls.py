
from . import views
from django.urls import path

from .views import ProfileView, EditProfileView

app_name = 'user_profile'

urlpatterns=[
    path('profile/', ProfileView.as_view(), name='profile_view'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
]