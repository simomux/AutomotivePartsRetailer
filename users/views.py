from datetime import timedelta
from functools import wraps

from django.contrib import messages
from django.http import HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views

from .forms import *
from .models import *


# Create your views here.

# Denies access to some view if the user is authenticated
class AuthenticatedUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseNotAllowed(['GET', 'POST'])
        return super().dispatch(request, *args, **kwargs)


# Decorator for FBV that checks if the user is not a staff member
def not_staff_user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_staff or not request.user.is_authenticated:
            return HttpResponseNotAllowed(['GET', 'POST'])
        return view_func(request, *args, **kwargs)

    return _wrapped_view


class UserLoginView(AuthenticatedUserMixin, auth_views.LoginView):
    def get_success_url(self):
        return reverse_lazy('profile')


# Compute scores for recommendation system for registered user
def compute_scores(user):
    scores = dict()
    user_items = CartItem.objects.filter(user=user).select_related('product__category', 'product__model__maker')

    for user_item in user_items:
        product = user_item.product
        category = product.category
        model = product.model
        maker = model.maker if model else None

        # If the items is bought from the user multiply it's score by 1.5x
        # If the user just added the item to the shopping cart multiply it's score by 1
        multiplier = 1.5 if user_item.order else 1

        # Scaling of scores to give priority to model before maker before category
        if category:
            scores[category.name] = round(scores.get(category.name, 0) + (user_item.quantity * multiplier * 0.8), 1)

        if maker:
            scores[maker.name] = round(scores.get(maker.name, 0) + (user_item.quantity * multiplier * 1), 1)

        if model:
            scores[model.name] = round(scores.get(model.name, 0) + (user_item.quantity * multiplier * 1.2), 1)

    return scores


class Profile(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'users/profile.html'
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_staff:
            scores = compute_scores(self.request.user)

            if scores:
                max_score_key = max(scores, key=scores.get)

                # Prioritize the filtering order
                resulting_set = Product.objects.filter(category__name=max_score_key)
                if not resulting_set.exists():
                    resulting_set = Product.objects.filter(model__name=max_score_key)
                if not resulting_set.exists():
                    resulting_set = Product.objects.filter(model__maker__name=max_score_key)

                # Randomize the items in the interested queryset and take 5 of them
                context["interest_list"] = resulting_set.order_by('?')[:4]
                context["interest"] = max_score_key

        return context


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

    total_price = 0
    for cart_item in cart_items:
        if cart_item.product.is_discount:
            total_price += cart_item.product.discount_price * cart_item.quantity
        else:
            total_price += cart_item.product.price * cart_item.quantity

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
        if cart_item.product.is_discount:
            sum_price += cart_item.product.discount_price * cart_item.quantity
        else:
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
                name=form.cleaned_data['name'],
                surname=form.cleaned_data['surname'],
                city=form.cleaned_data['city'],
                state=form.cleaned_data['state'],
                country=get_object_or_404(Country, name=form.cleaned_data['country']),
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                total_items=num_items,
                total_price=sum_price,
                estimated_time=1 + num_items if get_object_or_404(Country, name=form.cleaned_data[
                    'country']).name == "Italy" else None,
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

            messages.success(request, f'Your order was successful.')
            return redirect('profile')

    else:
        form = CheckoutForm()

    return render(request, 'users/order.html', {'form': form, 'sum_price': sum_price, 'num_items': num_items})


class OrderList(LoginRequiredMixin, ListView):
    model = Order
    template_name = "users/order_list.html"
    paginate_by = 10

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Order.objects.filter(user=self.request.user).order_by('-id')
        return Order.objects.all().order_by('-id')


class OrderDetail(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "users/order_detail.html"

    def get_queryset(self):
        if not self.request.user.is_staff:
            return Order.objects.filter(user=self.request.user)
        return Order.objects.all()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)

        if (obj.user != self.request.user) and not self.request.user.is_staff:
            return HttpResponseBadRequest("You do not have permission to view this order.")

        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_order = self.get_object()

        estimated = None
        if current_order.estimated_time:
            estimated = current_order.date_added + timedelta(days=current_order.estimated_time)

        items_set = CartItem.objects.filter(order=current_order)

        context['items_set'] = items_set
        context['estimated'] = estimated

        return context


def order_next(request, order_id):
    if request.user.is_staff:
        order = get_object_or_404(Order, pk=order_id)
        current_status = order.status.name
        # Possible statuses: ["Preparing", "Shipped", "Arrived"]

        if current_status == "Preparing":
            new_status = Status.objects.get(name="Shipped")
            order.status = new_status
            order.save()
        elif current_status == "Shipped":
            new_status = Status.objects.get(name="Arrived")
            order.status = new_status
            order.save()

        return redirect('orders')
    return HttpResponseBadRequest("Invalid request method")
