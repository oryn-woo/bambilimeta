from django.db import models

from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings



class Product(models.Model):
    name = models.CharField(max_length=255)
    seller = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    category = models.CharField(
        max_length=50,
        choices=[
            ("books", "Books & Stationery"),
            ("electronics", "Electronics"),
            ("kitchen", "Kitchenware"),
            ("furniture", "Furniture"),
            ("clothing", "Clothing")
        ]

    )
    condition = models.CharField(
        max_length=20,
        choices=[("new", "New"), ("used", "Used"), ("refurbished", "Refurbished")],
        default="used"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    description = models.TextField()
    is_student_discount = models.BooleanField(
        default=False,
        help_text="Flag if special student pricing applies"
    )
    pickup_location = models.CharField(
        max_length=100,
        default="On-campus"
    )
    delivery_available = models.BooleanField(default=False)
    warranty_period_months = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.seller.username}"


    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=0), name='price_greater_than_or_equal_to_zero'),
            models.CheckConstraint(condition=models.Q(stock__gte=0), name='stock_greater_than_or_equal_to_zero'),
        ]

    @property
    def is_available(self):
        """Returns True if the product is in stock."""
        return self.stock > 0

    @property
    def formatted_price(self):
        """Returns the formatted price as string with currency."""
        return f"${self.price:.2f}"

    @property
    def is_new(self):
        """Returns True if product was added in the last 30 days."""
        return self.created_at >= timezone.now() - timedelta(days=30)

    @property
    def valid_price(self):
        """Returns True if the price is a positive number."""
        return self.price > 0

    def get_absolute_url(self):
        """Returns the URL to access the product's detail page."""
        return reverse("market:product-detail", kwargs={"pk": self.pk})

    # def get_update_url(self):
    #     """Returns the URL to update the product."""
    #     return reverse("market:product_update", kwargs={"pk": self.pk})

    def get_display_name(self):
        return self.name.upper()


class ProductImage(models.Model):
    """
    Image associated with a product.

    Fields:
    - product: The product the image belongs to.
    - image: Actual image file.
    """
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images", blank=True, null=True)



class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='market_favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ('-created_at',)

