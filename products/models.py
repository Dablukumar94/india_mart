from django.db import models
from django.db.models import Avg
import uuid


# =========================
# PRODUCT
# =========================
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Main image
    main_image = models.ImageField(upload_to='products/', null=True, blank=True)

    # Extra fields (production ready)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    # ⭐ Average Rating
    @property
    def average_rating(self):
        avg = self.reviews.aggregate(avg=Avg("rating"))["avg"]
        return round(avg, 1) if avg else 0

    # ⭐ Rating Count
    @property
    def rating_count(self):
        return self.reviews.count()

    # 🖼️ Image fallback
    @property
    def display_image(self):
        if self.main_image:
            return self.main_image.url

        first_image = self.images.first()
        if first_image:
            return first_image.image.url

        return ""


# =========================
# PRODUCT IMAGE
# =========================
class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='products/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name