from functools import wraps

from django.contrib import messages
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views

from .forms import *
from .models import *


# Create your views here.

# Denies access to some view if the user is authenticated
class AuthenticatedUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # return redirect("home")
            return HttpResponseNotAllowed(['GET', 'POST'])
        return super().dispatch(request, *args, **kwargs)


def not_staff_user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff:
            return HttpResponseNotAllowed(['GET', 'POST'])
        return view_func(request, *args, **kwargs)

    return _wrapped_view


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


@not_staff_user_required
def cartView(request):
    cart_items = CartItem.objects.filter(user=request.user, order=None)

    # Check if the stock item of the items in the chart has been modified by someone else
    for cart_item in cart_items:
        current_product = get_object_or_404(Product, name=cart_item.product)
        if cart_item.quantity > current_product.stock:
            cart_item.quantity = current_product.stock
            cart_item.save()
            messages.warning(request, f'{cart_item.product} has reduced it\'s stock number.\nI will add to your cart '
                                      f'the new max number available of that product which is {current_product.stock}.')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, template_name='users/cart.html',
                  context={'cart_items': cart_items, 'total_price': total_price})


@not_staff_user_required
def add_to_cart(request, product_id):
    if request.method == "POST":
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                return HttpResponseBadRequest("Invalid quantity")
        except ValueError:
            return HttpResponseBadRequest("Invalid quantity")

        product = get_object_or_404(Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(product=product, user=request.user, order=None)
        cart_item.quantity += quantity
        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock
            messages.warning(request, 'You can\'t add more items that the max in stock!')
            return redirect('detail', product.id)

        user_cart_items = CartItem.objects.filter(user=request.user)
        max_sum = 0

        for item in user_cart_items:
            max_sum += item.quantity

        if (max_sum + cart_item.quantity) > 100:
            cart_item.quantity = 100 - max_sum
            if cart_item.quantity > 0:
                messages.warning(request, 'You can add up to max 100 items in your cart!')
                cart_item.save()
                return redirect('cart')
            else:
                messages.warning(request, 'Your cart is already full!')
                return redirect('detail', product.id)

        cart_item.save()

        messages.success(request, f'Added {quantity} {product.name}(s) to your cart.')
        return redirect('cart')

    return HttpResponseBadRequest("Invalid request method")


@not_staff_user_required
def remove_from_cart(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    cart_item.delete()
    return redirect('cart')


@not_staff_user_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user, order=None)

    if cart_items.count() <= 0:
        return HttpResponseBadRequest("Invalid request method")

    sum_price = 0
    num_items = 0
    for cart_item in cart_items:
        sum_price += cart_item.product.price * cart_item.quantity
        num_items += cart_item.quantity

    if request.method == 'POST':
        # Second check to make sure that while inputting shipping detail nobody bought the items
        for cart_item in cart_items:
            current_product = get_object_or_404(Product, name=cart_item.product)
            if cart_item.quantity > current_product.stock:
                cart_item.quantity = current_product.stock
                messages.warning(request, 'The number of items in stock changed!')
                return redirect('cart')

        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Create the order
            order = Order(
                user=request.user,
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                country=get_object_or_404(Country, name=form.cleaned_data['country']),
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                total_items=num_items,
                total_price=sum_price,
                status=get_object_or_404(Status, name='Preparing'),
                payment=get_object_or_404(Payment, name=form.cleaned_data['payment_method']),
            )
            order.save()

            # Assign to each CartItem the order
            for cart_item in cart_items:
                current_product = get_object_or_404(Product, name=cart_item.product)
                current_product.stock -= cart_item.quantity
                current_product.amount_bought += cart_item.quantity
                current_product.save()
                cart_item.order = order
                cart_item.save()

            #return redirect('order_detail', order.id)
            messages.success(request, f'Your order was successful.')
            return redirect('profile')

    else:
        form = CheckoutForm()

    return render(request, 'users/order.html', {'form': form, 'sum_price': sum_price, 'num_items': num_items})
