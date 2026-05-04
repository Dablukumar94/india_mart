from django.contrib.auth.models import User
from django.db import models
import uuid


class Order(models.Model):
    STATUS_CHOICES = (
        ('PLACED', 'Placed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURN_REQUESTED', 'Return Requested'),
        ('REPLACEMENT_REQUESTED', 'Replacement Requested'),
        ('PICKUP_SCHEDULED', 'Pickup Scheduled'),
        ('PICKED_UP', 'Picked Up'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )

    # =========================
    # 💰 PRICE SNAPSHOT (IMPORTANT)
    # =========================
    items_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # =========================
    # STATUS
    # =========================
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PLACED')

    delivered_at = models.DateTimeField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='order_items',
    )

    # =========================
    # 🧾 SNAPSHOT DATA
    # =========================
    product_name = models.CharField(max_length=255, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)  # freeze price
    product_image = models.CharField(max_length=500, blank=True, null=True)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
    

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")

    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)

    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.id} | {self.old_status} → {self.new_status}"