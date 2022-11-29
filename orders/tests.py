import datetime
from django.test import TestCase

from orders.factories import OrderFactory, OrderedProductFactory
from products.factories import ProductFactory
from app.factories import UserFactory
from rest_framework.test import APIClient
from orders.models import Order


class OrderAPITestCase(TestCase):

    def setUp(self):
        self.products = [ProductFactory() for _ in range(5)]
        self.user = UserFactory()
        self.user_2 = UserFactory()
        self.user_3 = UserFactory()
        self.orders = [
            OrderFactory(
                submitted_at=datetime.datetime.now(),
                user=self.user,
            ),
            OrderFactory(
                submitted_at=None,
                user=self.user,
            ),
            OrderFactory(
                user=self.user_2,
            )
        ]

    def test_get_all_orders_authenticated(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get('/orders/', format='json')
        self.assertEqual(len(response.data), 2)

    def test_get_all_orders_not_authenticated(self):
        client = APIClient()
        response = client.get('/orders/', format='json')
        self.assertEqual(response.status_code, 401)

    def test_get_current_order(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get('/orders/current/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.orders[1].id)

    def test_get_current_order_no_orders_present(self):
        client = APIClient()
        client.force_authenticate(user=self.user_3)
        orders_before = Order.objects.count()
        response = client.get('/orders/current/', format='json')
        self.assertEqual(response.status_code, 200)
        orders_after = Order.objects.count()
        self.assertEqual(orders_before + 1, orders_after)

    def test_submit_order_already_submitted(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        OrderedProductFactory(order=self.orders[0], product=self.products[3], quantity=1)
        response = client.post(f'/orders/{self.orders[0].id}/submit/', format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Order already submitted", str(response.content))

    def test_submit_order_empty(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(f'/orders/{self.orders[1].id}/submit/', format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Cannot submit an empty Order.", str(response.content))

    def test_submit_order(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        quantity_before = self.products[3].quantity_in_stock
        OrderedProductFactory(order=self.orders[1], product=self.products[3], quantity=1)
        response = client.post(f'/orders/{self.orders[1].id}/submit/', format='json')
        self.assertEqual(response.status_code, 200)
        self.products[3].refresh_from_db()
        quantity_after = self.products[3].quantity_in_stock
        self.assertEqual(quantity_before - 1, quantity_after)

    def test_submit_order_no_stock(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        self.products[3].quantity = 5
        self.products[3].save()
        OrderedProductFactory(order=self.orders[1], product__quantity_in_stock=5, quantity=10)
        response = client.post(f'/orders/{self.orders[1].id}/submit/', format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Not enough stock", str(response.content))
