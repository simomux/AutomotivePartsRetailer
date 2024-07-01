from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic import CreateView

from .forms import UserRegistrationForm
from .models import *


# Create your views here.

class Profile(ListView):
    model = None
    template_name = 'users/profile.html'


class Register(CreateView):
    form_class = UserRegistrationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("login")
