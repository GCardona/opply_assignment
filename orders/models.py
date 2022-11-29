from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q, UniqueConstraint


class OrderedProduct(models.Model):
    order = models.ForeignKey("orders.Order", null=False, on_delete=models.CASCADE)
    product = models.ForeignKey(
        "products.Product", null=False, on_delete=models.DO_NOTHING
    )
    quantity = models.PositiveIntegerField(null=False, default=1)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, default=Decimal("0.00")
    )
    submitted_at = models.DateTimeField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            UniqueConstraint(  # Only one non-submitted Order at a time.
                fields=["submitted_at"],
                condition=Q(submitted_at=None),
                name="unique_submitted_at_None",
            )
        ]
