from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms

from django.contrib.auth.forms import UserCreationForm
from .models import *


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Email: ', required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email or email.count('@') != 1 or ' ' in email:
            self.add_error('email', "Your email is invalid!")

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class CheckoutForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_show_errors = True
    helper.form_id = 'create-order'
    helper.form_method = "POST"
    helper.add_input(Submit("submit", "Order", css_class="nav-button"))

    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        label='Country',
        empty_label="Select a country",
        to_field_name='name',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    payment_method = forms.ModelChoiceField(
        queryset=Payment.objects.all(),
        label='Payment Method',
        empty_label="Select a category",
        to_field_name='name',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Order
        fields = ["city", "state", "country", "phone", "address", "payment_method"]
