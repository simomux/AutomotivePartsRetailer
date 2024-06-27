from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from products.models import Product


class HomePageView(ListView):
    template_name = 'products/home.html'
    model = Product


class DetailProductView(DetailView):
    model = Product
    template_name = 'products/detail.html'
