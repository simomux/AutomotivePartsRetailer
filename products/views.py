from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import *
from .forms import SearchForm


class HomePageView(ListView):
    template_name = 'products/home.html'
    model = Product


class DetailProductView(DetailView):
    model = Product
    template_name = 'products/detail.html'


def searchPage(request):
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            searchstring = form.cleaned_data['search_string']
            category = form.cleaned_data['search_category']
            maker = form.cleaned_data['search_maker']
            return redirect('search_results',  category, maker, searchstring)
    else:
        form = SearchForm()

    return render(request, template_name='products/search.html', context={"form": form})


class SearchResultsView(ListView):
    model = Product
    template_name = 'products/search_results.html'

    def get_queryset(self):
        search_string = self.request.resolver_match.kwargs.get('searchstring')
        print("String: " + search_string)
        search_category = self.request.resolver_match.kwargs.get('category')
        print("Category: " + search_category)
        if search_category == "None":
            search_category = None
        search_maker = self.request.resolver_match.kwargs.get('maker')
        print("Maker: " + search_maker)
        if search_maker == "None":
            search_maker = None

        # Get Category and CarModel instances based on search parameters
        category_instance = Category.objects.get(name=search_category) if search_category else None
        maker_instance = CarMaker.objects.get(name=search_maker) if search_maker else None
        model_instance = CarModel.objects.filter(maker=maker_instance)

        # Filter products based on search_string, category_instance, and maker_instance
        queryset = Product.objects.all()

        if search_string:
            queryset = queryset.filter(name__icontains=search_string)

        if category_instance:
            queryset = queryset.filter(category=category_instance)

        if maker_instance:
            queryset = queryset.filter(model__in=model_instance)

        return queryset
