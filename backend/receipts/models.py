import uuid
from django.db import models


class Item(models.Model):
    shortDescription = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    retailer = models.CharField(max_length=255)
    purchaseDate = models.DateField()
    purchaseTime = models.TimeField()
    items = models.ManyToManyField(Item)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Receipt {self.id}"
