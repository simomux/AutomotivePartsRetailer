from django import forms
from .models import *

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit


class SearchForm(forms.Form):
    # Initialize the form fields
    search_string = forms.CharField(label='Search string: ', max_length=100, min_length=3, required=False)
    search_category = forms.ChoiceField(label='Category: ', required=False)
    search_maker = forms.ChoiceField(label='Maker: ', required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        # Dynamically set the choices for the category field
        category_list = Category.objects.all()
        category_names = [(category.name, category.name) for category in category_list]
        category_names.sort()
        category_names.append(("None", '--'))

        self.fields['search_category'].choices = category_names
        self.fields['search_category'].initial = category_names[-1]

        maker_list = CarMaker.objects.all()
        maker_names = [(maker.name, maker.name) for maker in maker_list]
        maker_names.sort()
        maker_names.append(("None", '--'))
        maker_names.append(("Universal", 'Universal'))
        self.fields['search_maker'].choices = maker_names
        self.fields['search_maker'].initial = maker_names[-2]

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('search_string', css_class='form-control'),
            Field('search_category', css_class='form-control'),
            Field('search_maker', css_class='form-control')
        )

    def clean(self):
        cleaned_data = super().clean()
        search_category = cleaned_data.get('search_category')
        search_maker = cleaned_data.get('search_maker')

        if search_category == 'Tool' and search_maker != "None":
            self.add_error('search_maker', "You can only select '--' for Maker when searching in the 'Tool' category.")

        return cleaned_data


class CreateCountryForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_show_errors = True
    helper.form_id = 'create-country'
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Create", css_class="nav-button"))

    class Meta:
        model = Country
        fields = ["name"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if Country.objects.filter(name=name).exists():
            self.add_error('name', "A country with this name already exists.")

        return cleaned_data


class CreateMakerForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_show_errors = True
    helper.form_id = 'create-maker'
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Create", css_class="nav-button"))

    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        label='Country',
        empty_label="Select a country",
        to_field_name='name',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CarMaker
        fields = ["name", "country"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if CarMaker.objects.filter(name=name).exists():
            self.add_error('name', "A car maker with this name already exists.")

        return cleaned_data


class CreateModelForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_show_errors = True
    helper.form_id = 'create-model'
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Create", css_class="nav-button"))

    maker = forms.ModelChoiceField(
        queryset=CarMaker.objects.all(),
        label='Maker',
        empty_label="Select a maker",
        to_field_name='name',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CarModel
        fields = ["name", "maker"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if CarModel.objects.filter(name=name).exists():
            self.add_error('name', "A car model with this name already exists.")

        return cleaned_data


class CreateProductForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_show_errors = True
    helper.form_id = 'create-product'
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Create", css_class="nav-button"))
    image = forms.CharField(label='Image path (should start with imgs/)', required=False, max_length=100, min_length=5)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='Category',
        empty_label="Select a category",
        to_field_name='name',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    model = forms.ModelChoiceField(
        queryset=CarModel.objects.all(),
        label='Model',
        empty_label="Select a model",
        to_field_name='name',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "image", "is_discount", "discount_price", "category",
                  "model"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        category = Category.objects.get(name=cleaned_data.get('category')).name
        model = cleaned_data.get('model')
        is_discount = cleaned_data.get('is_discount')
        discount_price = cleaned_data.get('discount_price')

        if Product.objects.filter(name=name).exists():
            self.add_error('name', "A product with this name already exists.")

        if category == "Tool" and model is not None:
            self.add_error('model', "You can't select a model with this category.")

        if is_discount and discount_price is None:
            self.add_error('discount_price', "You must select a price for discount.")

        if discount_price is not None and not is_discount:
            self.add_error('is_discount', "You must check that the item is selected for discount.")

        return cleaned_data


class UpdateProductForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_show_errors = True
    helper.form_id = 'update-product'
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Update", css_class="nav-button"))
    image = forms.CharField(label='Image path', required=False, max_length=100, min_length=5)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label='Category',
        to_field_name='name',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    model = forms.ModelChoiceField(
        queryset=CarModel.objects.all(),
        label='Model',
        to_field_name='name',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        if instance:
            # Set initial value for category
            self.fields['category'].initial = instance.category.name

            # Set initial value for model
            if instance.model:
                self.fields['model'].initial = instance.model.name

    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock", "image", "is_discount", "discount_price", "category",
                  "model"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        category = Category.objects.get(name=cleaned_data.get('category')).name
        model = cleaned_data.get('model')
        is_discount = cleaned_data.get('is_discount')
        discount_price = cleaned_data.get('discount_price')

        if Product.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            self.add_error('name', "A product with this name already exists.")

        if category == "Tool" and model is not None:
            self.add_error('model', "You can't select a model with this category.")

        if is_discount and discount_price is None:
            self.add_error('discount_price', "You must select a price for discount.")

        if discount_price is not None and not is_discount:
            self.add_error('is_discount', "You must check that the item is selected for discount.")

        return cleaned_data


class UpdateModelForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_show_errors = True
    helper.form_id = 'update-model'
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Update", css_class="nav-button"))

    maker = forms.ModelChoiceField(
        queryset=CarMaker.objects.all(),
        label='Maker',
        empty_label="Select a maker",
        to_field_name='name',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CarModel
        fields = ["name", "maker"]

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')

        if CarModel.objects.filter(name=name).exclude(pk=self.instance.pk).exists():
            self.add_error('name', "A car model with this name already exists.")

        return cleaned_data
