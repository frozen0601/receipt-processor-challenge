from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
import math
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Receipt
from .serializers import ReceiptSerializer


class ReceiptViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["post"], url_path="process", name="process-receipt")
    @swagger_auto_schema(
        request_body=ReceiptSerializer, responses={201: openapi.Response("Created", ReceiptSerializer)}
    )
    @ratelimit(block=True)
    def process_receipt(self, request):
        """
        Submits a receipt for processing.
        """
        serializer = ReceiptSerializer(data=request.data)
        if serializer.is_valid():
            receipt = serializer.save()
            return Response({"id": str(receipt.id)}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"], url_path="points", name="get-points")
    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                "OK",
                openapi.Schema(
                    type=openapi.TYPE_OBJECT, properties={"points": openapi.Schema(type=openapi.TYPE_INTEGER)}
                ),
            )
        }
    )
    @ratelimit(block=True)
    def get_points(self, request, pk=None):
        """
        Returns the points awarded for the receipt.
        """
        try:
            receipt = Receipt.objects.get(pk=pk)
        except Receipt.DoesNotExist:
            return Response({"detail": "Receipt not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError:
            return Response({"detail": "Invalid receipt ID."}, status=status.HTTP_400_BAD_REQUEST)

        points = self.calculate_points(receipt)
        return Response({"points": points}, status=status.HTTP_200_OK)

    def calculate_points(self, receipt: Receipt) -> int:
        """
        Calculate the points for a given receipt based on predefined rules.
        """
        points = 0

        # One point for every alphanumeric character in the retailer name.
        points += sum(c.isalnum() for c in receipt.retailer)

        # 50 points if the total is a round dollar amount with no cents.
        if receipt.total == int(receipt.total):
            points += 50

        # 25 points if the total is a multiple of 0.25.
        if receipt.total % Decimal("0.25") == 0:
            points += 25

        # 5 points for every two items on the receipt.
        points += (len(receipt.items.all()) // 2) * 5

        # If the trimmed length of the item description is a multiple of 3,
        # multiply the price by 0.2 and round up to the nearest integer.
        for item in receipt.items.all():
            if len(item.shortDescription.strip()) % 3 == 0:
                points += math.ceil(float(item.price) * 0.2)

        # 6 points if the day in the purchase date is odd.
        if receipt.purchaseDate.day % 2 != 0:
            points += 6

        # 10 points if the time of purchase is after 2:00pm and before 4:00pm.
        if 14 <= receipt.purchaseTime.hour < 16:
            points += 10

        return points
