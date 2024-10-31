import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from .models import Receipt, Item
from decimal import Decimal
from datetime import datetime

# Constants
RECEIPT_DATA = {
    "retailer": "Target",
    "purchaseDate": "2022-01-01",
    "purchaseTime": "13:01",
    "items": [
        {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
        {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
        {"shortDescription": "Knorr Creamy Chicken", "price": "1.26"},
        {"shortDescription": "Doritos Nacho Cheese", "price": "3.35"},
        {"shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ", "price": "12.00"},
    ],
    "total": "35.35",
}


# Fixtures
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def receipt_data():
    return RECEIPT_DATA


# Factory Functions
def create_receipt(receipt_data):
    receipt = Receipt.objects.create(
        retailer=receipt_data["retailer"],
        total=Decimal(receipt_data["total"]),
        purchaseDate=datetime.strptime(receipt_data["purchaseDate"], "%Y-%m-%d").date(),
        purchaseTime=datetime.strptime(receipt_data["purchaseTime"], "%H:%M").time(),
    )
    for item_data in receipt_data["items"]:
        item = Item.objects.create(
            shortDescription=item_data["shortDescription"],
            price=Decimal(item_data["price"]),
        )
        receipt.items.add(item)
    return receipt


# Test Class
@pytest.mark.django_db
class TestReceiptViewSet:
    def test_process_receipt_success(self, api_client, receipt_data):
        """
        Test processing a valid receipt.
        """
        url = reverse("receipt-process-receipt")
        response = api_client.post(url, receipt_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data

    def test_process_receipt_invalid_data(self, api_client):
        """
        Test processing an invalid receipt.
        """
        url = reverse("receipt-process-receipt")
        response = api_client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_points_success(self, api_client, receipt_data):
        """
        Test retrieving points for a valid receipt.
        """
        receipt = create_receipt(receipt_data)
        url = reverse("receipt-get-points", args=[receipt.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert "points" in response.data

    def test_get_points_receipt_not_found(self, api_client):
        """
        Test retrieving points for a non-existent receipt.
        """
        url = reverse("receipt-get-points", args=["00000000-0000-0000-0000-000000000000"])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["detail"] == "Receipt not found."

    def test_get_points_example(self, api_client):
        """
        Test retrieving points for a specific example receipt.
        """
        receipt = create_receipt(RECEIPT_DATA)
        url = reverse("receipt-get-points", args=[receipt.id])
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {"points": 28}
