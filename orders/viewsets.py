from django.shortcuts import get_object_or_404
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet

from orders import services as order_services
from orders.models import Order


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "total_amount", "submitted_at", "orderedproduct_set", "created_at"]
        depth = 1


class OrderViewSet(ReadOnlyModelViewSet):
    authentication_classes = [BasicAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        # We just want to return the current user's Orders.
        return self.queryset.filter(user=self.request.user)

    @action(detail=False, methods=["get"])
    def current(self, request):
        return Response(
            OrderSerializer(
                instance=order_services.get_current_order(request.user.id)
            ).data
        )

    @action(detail=True, methods=["post"])
    def submit(self, request, pk=None):
        order = get_object_or_404(Order, id=pk)
        if order.submitted_at:
            raise ValidationError("Order already submitted.")

        try:
            order = order_services.submit_order(order.id)
        except (order_services.ProductNotInStock, order_services.EmptyOrder) as err:
            raise ValidationError(str(err))

        return Response(OrderSerializer(instance=order).data)
