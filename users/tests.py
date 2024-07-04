from django.http import HttpResponse
from django.test import TestCase, RequestFactory
from django.urls import reverse

from .views import *


# Create your tests here.

class ComputeScoresTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.country = Country.objects.create(name='UK')

        self.category1 = Category.objects.create(name='Spare part')
        self.maker1 = CarMaker.objects.create(name='Maker1', country=self.country)
        self.model1 = CarModel.objects.create(name='Model1', maker=self.maker1)
        self.product1 = Product.objects.create(name='Product1', category=self.category1, model=self.model1, price=100,
                                               stock=1)
        self.cart_item1 = CartItem.objects.create(user=self.user, product=self.product1, quantity=5)

        self.maker2 = CarMaker.objects.create(name='Maker2', country=self.country)
        self.model2 = CarModel.objects.create(name='Model2', maker=self.maker2)
        self.product2 = Product.objects.create(name='Product2', category=self.category1, model=self.model2, price=100,
                                               stock=1)
        self.cart_item2 = CartItem.objects.create(user=self.user, product=self.product2, quantity=3)

        self.payment = Payment.objects.create(name='Paypal')
        self.status = Status.objects.create(name='Preparing')

        self.order = Order.objects.create(user=self.user, name='Foo', surname='Foo',
                                          city='Foo', state='Foo', country=self.country, phone='foo', address='foo',
                                          total_items=5, total_price=5 * 100, payment=self.payment, status=self.status)

        self.cart_item2.order = self.order
        self.cart_item2.save()

    def test_compute_scores(self):
        scores = compute_scores(self.user)
        expected_scores = {
            'Spare part': 7.6,  # quantity * multiplier * weight = 5 * 1 * 0.8 + 3 * 1.5 * 0.8
            'Maker1': 5,  # quantity * multiplier * weight = 5 * 1 * 1
            'Model1': 6,  # quantity * multiplier * weight = 5 * 1 * 1.2
            'Maker2': 4.5,  # 3 * 1.5 * 1
            'Model2': 5.4,  # 3 * 1.5 * 1.2
        }
        self.assertEqual(scores, expected_scores)


class OrderDetailViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.country = Country.objects.create(name='UK')
        self.payment = Payment.objects.create(name='Paypal')
        self.status = Status.objects.create(name='Preparing')
        self.status = Status.objects.create(name='Preparing')
        self.order = Order.objects.create(user=self.user, name='Foo', surname='Foo',
                                          city='Foo', state='Foo', country=self.country, phone='foo', address='foo',
                                          total_items=5, total_price=5 * 100, payment=self.payment, status=self.status)

    def test_order_detail_view(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/order_detail.html')
        self.assertContains(response, self.order.status.name)

    # Code error is 404 instead of 400 because the queryset only contains the user's orders.
    def test_order_detail_view_unauthorized(self):
        other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.get(reverse('order_detail', args=[self.order.id]))
        self.assertEqual(response.status_code, 404)


class NotStaffUserRequiredTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.staff_user = User.objects.create_user(username='staffuser', password='staffpass', is_staff=True)
        self.non_staff_user = User.objects.create_user(username='nonstaffuser', password='nonstaffpass')

    def test_not_staff_user_required_with_staff_user(self):
        request = self.factory.get('/dummy-url/')
        request.user = self.staff_user
        response = not_staff_user_required(lambda req: HttpResponse('OK'))(request)
        self.assertEqual(response.status_code, 405)

    def test_not_staff_user_required_with_non_staff_user(self):
        request = self.factory.get('/dummy-url/')
        request.user = self.non_staff_user
        response = not_staff_user_required(lambda req: HttpResponse('OK'))(request)
        self.assertEqual(response.status_code, 200)
