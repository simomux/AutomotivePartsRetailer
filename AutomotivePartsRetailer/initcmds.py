import os.path

from products.models import *
from users.models import *

from csv import reader


def erase_db():
    print('Erasing DB')
    Product.objects.all().delete()
    CarMaker.objects.all().delete()
    CarModel.objects.all().delete()
    Country.objects.all().delete()


def init_db():
    print('Initializing DB')

    if len(Category.objects.all()) == 0:
        # Categories of listed items
        list_categories = ["Spare part", "Tool", "Accessory"]

        # Adding Categories to the DB
        for i in list_categories:
            cat = Category(name=i)
            cat.save()

    if len(Payment.objects.all()) == 0:
        list_payments = ["Apple Pay", "PayPal", "Credit card/Debit card", "Wire transfer"]

        for i in list_payments:
            pay = Payment(name=i)
            pay.save()

    if len(Status.objects.all()) == 0:
        list_order_status = ["Preparing", "Shipped", "Arrived"]

        for i in list_order_status:
            status = Status(name=i)
            status.save()

    # Main countries of car manufacturers
    if len(Country.objects.all()) == 0:
        with open("static/data/countries.csv") as manufacturers:
            csv_reader = reader(manufacturers, delimiter=',')
            for row in csv_reader:
                country = Country(name=row[0])
                country.save()

    if len(CarMaker.objects.all()) == 0:
        # Reading main car brands and pairing them to the respective countries
        with open("static/data/manufacturers.csv") as manufacturers:
            csv_reader = reader(manufacturers, delimiter=',')
            for row in csv_reader:
                country = Country.objects.get(name=row[1])
                maker = CarMaker(name=row[0], country=country)
                maker.save()

    if len(CarModel.objects.all()) == 0:
        # Reading car models and pairing them to the respective manufacturers
        with open("static/data/models.csv") as models:
            csv_reader = reader(models, delimiter=',')
            for row in csv_reader:
                maker = CarMaker.objects.get(name=row[1])
                car_model = CarModel(name=row[0], maker=maker)
                car_model.save()

    if len(Product.objects.all()) == 0:
        # Adding manually some products to the DB -- still in testing
        with open("static/data/products.csv") as products:
            csv_reader = reader(products, delimiter=',')
            for i in csv_reader:
                name = i[0].strip()
                description = i[1].strip()
                price = i[2].strip()
                stock = i[3].strip()
                category = Category.objects.get(name=i[4].strip())
                image = os.path.join("imgs/", i[0].replace(" ", "_")+".webp")

                if category != "Tool":
                    try:
                        model = CarModel.objects.get(name=i[5].strip())
                    except CarModel.DoesNotExist:
                        model = None

                if i[-2].strip() == "True":
                    discount_price = i[-1].strip()
                    product = Product(name=name, description=description, price=price, stock=stock, category=category, model=model, image=image, is_discount=True, discount_price=discount_price)
                else:
                    product = Product(name=name, description=description, price=price, stock=stock, category=category, model=model, image=image)

                product.save()
