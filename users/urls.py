from django.urls import path

from .views import *

urlpatterns = [
    path('profile/', Profile.as_view(), name='profile'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', Register.as_view(), name='register'),

    # Cart views
    path('cart/', cartView, name='cart'),
    path('cart/add_item/<int:product_id>', add_to_cart, name='add_item'),
    path('cart/remove_item/<int:item_id>', remove_from_cart, name='remove_item'),

    # Checkout view
    path('checkout/', checkout, name='checkout'),
]
