from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReceiptViewSet

router = DefaultRouter()
router.register(r"receipts", ReceiptViewSet, basename="receipt")

urlpatterns = [
    path("", include(router.urls)),
    path("receipts/<uuid:pk>/points/", ReceiptViewSet.as_view({"get": "get_points"}), name="receipt-points"),
]
