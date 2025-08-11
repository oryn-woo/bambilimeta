from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User


class House(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Ensures no negative prices.
    house_desc = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    # image = models.ImageField(upload_to="house_images/", blank=True, null=True, default="default.jpeg")
    video = models.FileField(upload_to="house_videos/", blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)  # Number of times the house has been viewed, help in cache

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("housing:house_detail", kwargs={"pk": self.pk})


class HouseImage(models.Model):
    house = models.ForeignKey(House, related_name="images", on_delete=models.CASCADE)
    # related_name argument, allows  queries.
    image = models.ImageField(upload_to="house_images")


class HouseReview(models.Model):
    house = models.ForeignKey(House, related_name="reviews", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveIntegerField()
    reviewed_on = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        return self.house.get_absolute_url()
        # return reverse("housing:house_detail", kwargs={"pk": self.house.pk})


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites", null=False, blank=False)
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="favorites", null=False, blank=False)
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "house")  # Prevent duplicate favorites

    def __str__(self):
        return f"{self.user.username} - {self.house.title} (Favorited on {self.favorited_at})"

