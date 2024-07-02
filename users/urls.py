from django.urls import path

from .views import *

urlpatterns = [
    path('profile/', Profile.as_view(), name='profile'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', Register.as_view(), name='register'),
]