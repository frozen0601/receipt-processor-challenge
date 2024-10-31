from rest_framework import serializers
from .models import Receipt, Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ["shortDescription", "price"]


class ReceiptSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)

    class Meta:
        model = Receipt
        fields = ["id", "retailer", "purchaseDate", "purchaseTime", "items", "total"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        receipt = Receipt.objects.create(**validated_data)
        for item_data in items_data:
            item = Item.objects.create(**item_data)
            receipt.items.add(item)
        return receipt
