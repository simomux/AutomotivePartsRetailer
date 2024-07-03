from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView

from .models import *
from .forms import *


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
    page_title = "Search results"

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['list_type'] = "search"
        return context


class ProductListView(ListView):
    model = Product
    paginate_by = 5
    template_name = 'products/products_list.html'
    page_title = ""
    list_type = ""

    def get_queryset(self):
        self.list_type = self.request.GET.get('type')
        if self.list_type == 'discounted':
            self.page_title = 'List of all discounted products'
            return Product.objects.filter(is_discount=True).order_by('?')
        elif self.list_type == 'mostsold':
            self.page_title = 'List of most sold products'
            return Product.objects.exclude(amount_bought=0).order_by('-amount_bought')
        else:
            self.page_title = 'List of all products'
            return Product.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['list_type'] = self.list_type

        return context


# Products management views
class StaffUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_authenticated and request.user.is_staff):
            # return redirect("home")
            return HttpResponseNotAllowed(['GET', 'POST'])
        return super().dispatch(request, *args, **kwargs)


class RemoveCountry(StaffUserMixin, DeleteView):
    model = Country
    template_name = "products/admin_manager/remove_item.html"
    success_url = reverse_lazy('staff_list', kwargs={'type': 'country'})
    type = ""

    def get_context_data(self, **kwargs):
        self.type = "country"
        context = super().get_context_data(**kwargs)
        context['type'] = self.type
        return context


class RemoveProduct(StaffUserMixin, DeleteView):
    model = Product
    template_name = "products/admin_manager/remove_item.html"
    success_url = reverse_lazy('staff_list', kwargs={'type': 'product'})
    type = ""

    def get_context_data(self, **kwargs):
        self.type = "product"
        context = super().get_context_data(**kwargs)
        context['type'] = self.type
        return context


class RemoveMaker(StaffUserMixin, DeleteView):
    model = CarMaker
    template_name = "products/admin_manager/remove_item.html"
    success_url = reverse_lazy('staff_list', kwargs={'type': 'maker'})
    type = ""

    def get_context_data(self, **kwargs):
        self.type = "maker"
        context = super().get_context_data(**kwargs)
        context['type'] = self.type
        return context


class RemoveModel(StaffUserMixin, DeleteView):
    model = CarModel
    template_name = "products/admin_manager/remove_item.html"
    success_url = reverse_lazy('staff_list', kwargs={'type': 'model'})
    type = ""

    def get_context_data(self, **kwargs):
        self.type = "model"
        context = super().get_context_data(**kwargs)
        context['type'] = self.type
        return context


class AddCountry(StaffUserMixin, CreateView):
    template_name = "products/admin_manager/add_item.html"
    form_class = CreateCountryForm
    success_url = reverse_lazy('staff_list', kwargs={'type': 'country'})
    type = ""
    action = ""

    def get_context_data(self, **kwargs):
        self.type = "country"
        self.action = "Create"
        context = super().get_context_data(**kwargs)
        context['type'] = self.type
        context['action'] = self.action
        context['form'] = self.form_class(self.request.POST or None)
        return context


class AddProduct(StaffUserMixin, CreateView):
    template_name = "products/admin_manager/add_item.html"
    form_class = CreateProductForm
    success_url = reverse_lazy('staff_list', kwargs={'type': 'product'})
    type = ""
    action = ""

    def get_context_data(self, **kwargs):
        self.type = "product"
        self.action = "Create"
        context = super().get_context_data(**kwargs)
        context['type'] = self.type
        context['action'] = self.action
        context['form'] = self.form_class(self.request.POST or None)
        return context


class AddMaker(StaffUserMixin, CreateView):
    template_name = "products/admin_manager/add_item.html"
    form_class = CreateMakerForm
    success_url = reverse_lazy('staff_list', kwargs={'type': 'maker'})
    type = ""
    action = ""

    def get_context_data(self, **kwargs):
        self.type = "maker"
        self.action = "Create"
        context = super().get_context_data(**kwargs)
        context['type'] = self.type
        context['action'] = self.action
        context['form'] = self.form_class(self.request.POST or None)
        return context


class AddModel(StaffUserMixin, CreateView):
    template_name = "products/admin_manager/add_item.html"
    form_class = CreateModelForm
    success_url = reverse_lazy('staff_list', kwargs={'type': 'model'})
    type = ""
    action = ""

    def get_context_data(self, **kwargs):
        self.type = "model"
        self.action = "Create"
        context = super().get_context_data(**kwargs)
        context['type'] = self.type
        context['action'] = self.action
        context['form'] = self.form_class(self.request.POST or None)
        return context


class ModifyProduct(StaffUserMixin, UpdateView):
    model = Product
    form_class = UpdateProductForm
    template_name = 'products/admin_manager/add_item.html'
    success_url = reverse_lazy('staff_list', kwargs={'type': 'product'})
    type = ""
    action = ""

    def get_context_data(self, **kwargs):
        self.type = "product"
        self.action = "Update"
        context = super().get_context_data(**kwargs)
        context['type'] = self.type
        context['action'] = self.action
        return context

    def get_queryset(self):
        return Product.objects.filter(pk=self.kwargs['pk'])

    def get_initial(self):
        initial = super().get_initial()

        instance = self.get_object()
        if instance:
            initial['model'] = instance.model
            initial['category'] = instance.category
        return initial


class ModifyModel(StaffUserMixin, UpdateView):
    model = CarModel
    form_class = UpdateModelForm
    template_name = 'products/admin_manager/add_item.html'
    success_url = reverse_lazy('staff_list', kwargs={'type': 'model'})
    type = ""
    action = ""

    def get_context_data(self, **kwargs):
        self.type = "model"
        self.action = "Update"
        context = super().get_context_data(**kwargs)
        context['type'] = self.type
        context['action'] = self.action
        return context

    def get_queryset(self):
        return CarModel.objects.filter(pk=self.kwargs['pk'])

    def get_initial(self):
        initial = super().get_initial()

        instance = self.get_object()
        if instance:
            initial['maker'] = instance.maker
        return initial


# ListView of table elements for CRUD operations
class TableList(StaffUserMixin, ListView):
    list_type = ""
    paginate_by = 20
    template_name = "products/admin_manager/table_list.html"

    def get_queryset(self):
        self.list_type = self.request.resolver_match.kwargs.get('type')

        if self.list_type == 'country':
            return Country.objects.all().order_by('-id')
        elif self.list_type == 'maker':
            return CarMaker.objects.all().order_by('-id')
        elif self.list_type == 'model':
            return CarModel.objects.all().order_by('-id')
        elif self.list_type == 'product':
            return Product.objects.all().order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_type'] = self.list_type

        return context
