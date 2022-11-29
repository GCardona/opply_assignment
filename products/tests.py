from django.test import TestCase
from products.factories import ProductFactory
from app.factories import UserFactory
from rest_framework.test import APIClient
from orders.models import Order


class ProductAPITestCase(TestCase):

    def setUp(self):
        self.products = [ProductFactory() for _ in range(5)]
        self.user = UserFactory()

    def test_get_all_products_authenticated(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get('/products/', format='json')
        self.assertEqual(len(response.data), 5)

    def test_get_all_products_not_authenticated(self):
        client = APIClient()
        response = client.get('/products/', format='json')
        self.assertEqual(response.status_code, 401)

    def test_get_all_products_no_stock(self):
        self.products[0].quantity_in_stock = 0
        self.products[0].save()
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get('/products/', format='json')
        self.assertEqual(len(response.data), 4)

    def test_add_product_to_order(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(f'/products/{self.products[0].id}/add_to_order/', format='json')
        self.assertEqual(response.status_code, 200)
        order_id = response.data["order_id"]
        order = Order.objects.get(id=order_id)
        self.assertEqual(Order.objects.count(), 1)
        self.assertIsNone(order.submitted_at)
        self.assertEqual(order.orderedproduct_set.count(), 1)
        self.assertEqual(order.orderedproduct_set.first().product_id, self.products[0].id)
        self.assertEqual(order.orderedproduct_set.first().quantity, 1)

        # Add one more from same product
        response = client.post(f'/products/{self.products[0].id}/add_to_order/', format='json')
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.orderedproduct_set.first().product_id, self.products[0].id)
        self.assertEqual(order.orderedproduct_set.first().quantity, 2)

        # Add one more from different product
        response = client.post(f'/products/{self.products[1].id}/add_to_order/', format='json')
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.orderedproduct_set.count(), 2)

    def test_add_product_to_order_no_stock(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        self.products[0].quantity_in_stock = 0
        self.products[0].save()
        response = client.post(f'/products/{self.products[0].id}/add_to_order/', format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Not enough stock.", str(response.content))

    def test_remove_product_from_order(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(f'/products/{self.products[0].id}/add_to_order/', format='json')
        self.assertEqual(response.status_code, 200)
        order_id = response.data["order_id"]
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.orderedproduct_set.count(), 1)
        # Remove Product.
        response = client.post(f'/products/{self.products[0].id}/remove_from_order/', format='json')
        self.assertEqual(order.orderedproduct_set.count(), 0)

    def test_remove_product_from_empty_order(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(f'/products/{self.products[0].id}/add_to_order/', format='json')
        self.assertEqual(response.status_code, 200)
        order_id = response.data["order_id"]
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.orderedproduct_set.count(), 1)
        # Remove Product.
        response = client.post(f'/products/{self.products[0].id}/remove_from_order/', format='json')
        self.assertEqual(order.orderedproduct_set.count(), 0)

        response = client.post(f'/products/{self.products[0].id}/remove_from_order/', format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Product not currently in the active Order.", str(response.content))
