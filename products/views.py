from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import *
from .forms import SearchForm


class HomePageView(ListView):
    template_name = 'products/home.html'
    model = Product

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Preview list of all items
        context['products'] = Product.objects.all().order_by('?')[:4]

        # Preview list of discounted items
        context['discounted_products'] = Product.objects.filter(is_discount=True).order_by('?')[:4]

        # Preview list of most sold items (items must have been sold at least 1 time)
        context['most_sold'] = Product.objects.exclude(amount_bought=0).order_by('-amount_bought')[:4]
        return context


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
            if searchstring == "":
                searchstring = "None"
            return redirect('search_results', category, maker, searchstring)
    else:
        form = SearchForm()

    return render(request, template_name='products/search.html', context={"form": form})


class SearchResultsView(ListView):
    model = Product
    template_name = 'products/products_list.html'
    paginate_by = 5

    def get_queryset(self):
        search_string = self.request.resolver_match.kwargs.get('searchstring')
        if search_string == "None":
            search_string = None
        search_category = self.request.resolver_match.kwargs.get('category')
        if search_category == "None":
            search_category = None
        search_maker = self.request.resolver_match.kwargs.get('maker')
        if search_maker == "None":
            search_maker = None

        maker_instance = model_instance = None
        category_instance = Category.objects.get(name=search_category) if search_category else None
        try:
            if search_maker != "Universal":
                maker_instance = CarMaker.objects.get(name=search_maker) if search_maker else None
                model_instance = CarModel.objects.filter(maker=maker_instance)
        except (CarMaker.DoesNotExist, CarModel.DoesNotExist, Category.DoesNotExist):
            pass

        # Filter products based on search_string, category_instance, and model_instance
        queryset = Product.objects.all()

        if search_string:
            queryset = queryset.filter(name__icontains=search_string)

        if category_instance:
            queryset = queryset.filter(category=category_instance)

        if maker_instance:
            queryset = queryset.filter(model__in=model_instance)

        if search_maker == "Universal":
            queryset = queryset.exclude(category=Category.objects.get(name="Tool"))
            queryset = queryset.filter(model=None)

        return queryset


class ProductListView(ListView):
    model = Product
    paginate_by = 5
    template_name = 'products/products_list.html'
    page_title = ""
    page_subtitle = ""

    def get_queryset(self):
        list_type = self.request.GET.get('type')

        if list_type == 'discounted':
            self.page_title = 'Discounted'
            self.page_subtitle = 'all discounted'
            return Product.objects.filter(is_discount=True).order_by('?')
        elif list_type == 'mostsold':
            self.page_title = 'Most sold'
            self.page_subtitle = 'most sold'
            return Product.objects.exclude(amount_bought=0).order_by('-amount_bought')
        else:
            self.page_title = 'All'
            self.page_subtitle = 'all'
            return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['page_subtitle'] = self.page_subtitle
        return context
