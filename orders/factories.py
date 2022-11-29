import factory

from app.factories import UserFactory
from orders.models import Order, OrderedProduct
from products.factories import ProductFactory


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)


class OrderedProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderedProduct

    order = factory.SubFactory(OrderFactory)
    product = factory.SubFactory(ProductFactory)
    quantity = factory.Sequence(lambda n: n + 1)
