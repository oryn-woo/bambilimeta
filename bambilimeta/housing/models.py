from django.db import models
from django.utils import timezone
from django.urls import reverse


class House(models.Model):
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Ensures no negative prices.
    house_desc = models.TextField()
    created_at = models.DateTimeField(default=timezone.now())
    image = models.ImageField(upload_to="house_images/", blank=True, null=True)
    video = models.FileField(upload_to="house_videos/", blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("house_detail", kwargs={"pk": self.pk})
