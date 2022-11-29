import decimal
import factory
from products.models import Product


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n + 1}")
    price = factory.Sequence(lambda n: decimal.Decimal(n + 1))
    quantity_in_stock = factory.Sequence(lambda n: n + 1)
