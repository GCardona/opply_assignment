import datetime
from django.contrib.auth.models import User

from orders.models import Order, OrderedProduct
from products.models import Product


class ProductNotInOrder(Exception):
    pass


class ProductNotInStock(Exception):
    pass


class EmptyOrder(Exception):
    pass


def get_current_order(user_id: int):
    order, created = Order.objects.get_or_create(
        user_id=user_id,
        submitted_at=None,
        defaults={
            "user": User.objects.get(id=user_id),
        },
    )
    return order


def order_product(user_id: int, product_id: int):
    order = get_current_order(user_id)
    product = Product.objects.get(id=product_id)
    if product.quantity_in_stock == 0:
        raise ProductNotInStock

    ordered_product, created = OrderedProduct.objects.get_or_create(
        product_id=product_id,
        order_id=order.id,
    )  # `quantity` is 1 by default.

    if not created:  # We need to increment quantity if already existent.
        ordered_product.quantity = ordered_product.quantity + 1
        ordered_product.save()

    order.total_amount += ordered_product.product.price
    order.save()
    return order.id


def unorder_product(user_id: int, product_id: int):
    order = get_current_order(user_id)
    try:
        ordered_product = OrderedProduct.objects.get(
            product_id=product_id,
            order_id=order.id,
        )
    except OrderedProduct.DoesNotExist:
        raise ProductNotInOrder

    order.total_amount -= ordered_product.product.price
    order.save()

    if ordered_product.quantity == 1:
        ordered_product.delete()
    else:
        ordered_product.quantity -= 1
        ordered_product.save()

    return order.id


def submit_order(order_id):
    order = Order.objects.get(id=order_id)
    if order.orderedproduct_set.count() == 0:
        raise EmptyOrder("Cannot submit an empty Order.")

    for ordered_product in order.orderedproduct_set.all():
        if ordered_product.product.quantity_in_stock < ordered_product.quantity:
            raise ProductNotInStock(
                f"Not enough stock of product {ordered_product.product.id}. "
                f"Remove or lower the quantity."
            )
        ordered_product.product.quantity_in_stock -= ordered_product.quantity
        ordered_product.product.save()

    order.submitted_at = datetime.datetime.now()
    order.save()
    return order
