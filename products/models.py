from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Country(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Countries"

    def __str__(self):
        return self.name


class CarMaker(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Makers"

    def __str__(self):
        return self.name


class CarModel(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    maker = models.ForeignKey(CarMaker, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Models"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.CharField(max_length=100, blank=True, null=True)

    # Field used to keep track of how many times an item is sold. This is used for the recommendation system based on
    # the most sold items
    amount_bought = models.PositiveIntegerField(default=0)

    # These fields are used to keep track of the new price, if the item is on discount.
    # This is also used for the recommendation system based on discounted items.
    is_discount = models.BooleanField(default=False)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # If the model field is null and the product is category "spare part" we consider it a universal spare part
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name
