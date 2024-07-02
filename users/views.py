from django.http import HttpResponseNotAllowed
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views

from .forms import UserRegistrationForm
from .models import *


# Create your views here.

# Denies access to some view if the user is authenticated
class AuthenticatedUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # return redirect("home")
            return HttpResponseNotAllowed(['GET', 'POST'])
        return super().dispatch(request, *args, **kwargs)


class UserLoginView(AuthenticatedUserMixin, auth_views.LoginView):
    def get_success_url(self):
        return reverse_lazy('profile')


class Profile(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user


# A user already authenticated cannot register another user
class Register(AuthenticatedUserMixin, CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")
