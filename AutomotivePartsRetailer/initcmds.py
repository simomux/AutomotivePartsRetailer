import os.path

from products.models import Product, CarModel, CarMaker, Category, Country
from csv import reader


def erase_db():
    print('Erasing DB')
    Category.objects.all().delete()
    Product.objects.all().delete()
    CarMaker.objects.all().delete()
    CarModel.objects.all().delete()
    Country.objects.all().delete()


def init_db():
    print('Initializing DB')
    if len(Category.objects.all()) != 0 and len(Country.objects.all()) != 0:
        return

    # Categories of listed items
    list_categories = ["Spare part", "Tool", "Accessory"]

    # Adding Categories to the DB
    for i in list_categories:
        cat = Category(name=i)
        cat.save()

    # Main countries of car manufacturers
    with open("static/data/countries.csv") as manufacturers:
        csv_reader = reader(manufacturers, delimiter=',')
        for row in csv_reader:
            country = Country(name=row[0])
            country.save()

    # Reading main car brands and pairing them to the respective countries
    with open("static/data/manufacturers.csv") as manufacturers:
        csv_reader = reader(manufacturers, delimiter=',')
        for row in csv_reader:
            country = Country.objects.get(name=row[1])
            maker = CarMaker(name=row[0], country=country)
            maker.save()

    # Reading car models and pairing them to the respective manufacturers
    with open("static/data/models.csv") as models:
        csv_reader = reader(models, delimiter=',')
        for row in csv_reader:
            maker = CarMaker.objects.get(name=row[1])
            car_model = CarModel(name=row[0], maker=maker)
            car_model.save()

    # Adding manually some products to the DB -- still in testing
    with open("static/data/products.csv") as products:
        csv_reader = reader(products, delimiter=',')
        for i in csv_reader:
            print(i)
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
