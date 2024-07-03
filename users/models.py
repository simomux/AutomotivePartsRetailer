from django.contrib.auth.models import User

from products.models import *

from django.utils import timezone


# Create your models here.

class Status(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Statuses'


class Payment(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    surname = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    phone = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    total_items = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_time = models.PositiveIntegerField(null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} {self.pk}'


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'
