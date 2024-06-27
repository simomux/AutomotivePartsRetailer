from django.contrib import admin

from products.models import Product, Category, CarModel, CarMaker, Country

# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(CarModel)
admin.site.register(CarMaker)
admin.site.register(Country)