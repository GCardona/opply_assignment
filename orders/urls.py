from django.urls import include, path
from rest_framework.routers import DefaultRouter

from orders.viewsets import OrderViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="orders")

urlpatterns = [path("", include(router.urls))]
