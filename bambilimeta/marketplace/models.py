from django.db import models

from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=255)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-created_at']
        indexes = [ # Indexes speed up database query. e.g., Product.objects.filter(name__icontains="shoe")
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=["created_at"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price__gte=0),
                name='price_greater_than_or_equal_to_zero'
            ),
            models.CheckConstraint(
                condition=models.Q(stock__gte=0),
                name='stock_greater_than_or_equal_to_zero'
            ),
        ]

    @property
    def is_available(self):
        return self.stock > 0
    
    @property
    def formatted_price(self):
        return f"${self.price:.2f}"
    
    @property
    def is_new(self):
        """ Check if the product is new (created within the last 30 days)."""
        return (self.created_at >= timezone.now() - timedelta(days=30))
    
    @property
    def valid_price(self):
        """ Ensure the price is a valid positive number."""
        return self.price > 0

    def get_absolute_url(self):
        return reverse("market:product_detail", kwargs={"pk": self.pk})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="product_images", blank=True, null=True)
