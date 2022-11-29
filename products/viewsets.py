from django.shortcuts import get_object_or_404
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from orders import services as order_services
from products.models import Product


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class ProductViewSet(ModelViewSet):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.filter(quantity_in_stock__gt=0)
    serializer_class = ProductSerializer

    @action(detail=True, methods=["post"])
    def add_to_order(self, request, pk=None):
        user = request.user
        if not pk:
            raise ValidationError("Must specify a product id.")

        product = get_object_or_404(Product, id=pk)
        try:
            order_id = order_services.order_product(user.id, product.id)
        except order_services.ProductNotInStock:
            raise ValidationError("Cannot add product to Order. Not enough stock.")

        return Response({"order_id": order_id})

    @action(detail=True, methods=["post"])
    def remove_from_order(self, request, pk=None):
        user = request.user
        if not pk:
            raise ValidationError("Must specify a product id.")

        product = get_object_or_404(Product, id=pk)
        try:
            order_id = order_services.unorder_product(user.id, product.id)
        except order_services.ProductNotInOrder:
            raise NotFound("Product not currently in the active Order.")

        return Response({"order_id": order_id})
