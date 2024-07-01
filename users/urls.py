from django.urls import path

from django.contrib.auth import views as auth_views

from users import views

urlpatterns = [
    path('profile/', views.Profile.as_view(), name='profile'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.Register.as_view(), name='register'),
]