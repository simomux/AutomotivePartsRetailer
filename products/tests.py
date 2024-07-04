from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import *

# Create your tests here.


class AddProductViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(username='staffuser', password='staffpass', is_staff=True)
        self.non_staff_user = User.objects.create_user(username='nonstaffuser', password='nonstaffpass')
        self.category = Category.objects.create(name='Test Category')
        self.country = Country.objects.create(name='Test Country')
        self.maker = CarMaker.objects.create(name='Test Maker', country=self.country)
        self.model = CarModel.objects.create(name='Test Model', maker=self.maker)

    def test_add_product_with_staff_user(self):
        self.client.login(username='staffuser', password='staffpass')
        response = self.client.post(reverse('add_product'), {
            'name': 'Test Product',
            'description': 'Test Description',
            'category': 'Test Category',
            'model': 'Test Model',
            'price': 10.0,
            'stock': 5,
        })

        print(response.content)  # Debug response content

        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Product.objects.filter(name='Test Product').exists())

    def test_add_product_with_non_staff_user(self):
        self.client.login(username='nonstaffuser', password='nonstaffpass')
        response = self.client.post(reverse('add_product'), {
            'name': 'Test Product',
            'description': 'Test Description',
            'category': 'Test Category',
            'model': 'Test Model',
            'price': 10.0,
            'stock': 5,
        })
        self.assertEqual(response.status_code, 405)  # HttpResponseNotAllowed
        self.assertFalse(Product.objects.filter(name='Test Product').exists())


class RemoveProductViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(username='staffuser', password='staffpass', is_staff=True)
        self.non_staff_user = User.objects.create_user(username='nonstaffuser', password='nonstaffpass')
        self.category = Category.objects.create(name='Test Category')
        self.country = Country.objects.create(name='Test Country')
        self.maker = CarMaker.objects.create(name='Test Maker', country=self.country)
        self.model = CarModel.objects.create(name='Test Model', maker=self.maker)
        self.product = Product.objects.create(
            name='Test Product', category=self.category, model=self.model,
            price=10.0, stock=5, is_discount=False
        )

    def test_remove_product_with_staff_user(self):
        self.client.login(username='staffuser', password='staffpass')
        response = self.client.post(reverse('remove_product', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(name='Test Product').exists())

    def test_remove_product_with_non_staff_user(self):
        self.client.login(username='nonstaffuser', password='nonstaffpass')
        response = self.client.post(reverse('remove_product', kwargs={'pk': self.product.pk}))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Product.objects.filter(name='Test Product').exists())
