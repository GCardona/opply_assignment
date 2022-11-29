from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=1024, null=False, blank=False)
    price = models.DecimalField(null=False, blank=False, decimal_places=2, max_digits=7)
    quantity_in_stock = models.PositiveIntegerField(null=False, blank=False)
