from django.urls import path

from products import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('product/<pk>', views.DetailProductView.as_view(), name='detail'),
]
