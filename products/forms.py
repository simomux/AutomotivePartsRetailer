from django import forms
from django.shortcuts import get_object_or_404
from .models import Category, CarMaker

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

