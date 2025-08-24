from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User



class House(models.Model):
    title = models.CharField(max_length=100)
    owner = models.ForeignKey(User, related_name="houses", on_delete=models.CASCADE)
    location = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    house_desc = models.TextField( )
    num_bedrooms = models.PositiveSmallIntegerField(default=1)
    num_bathrooms = models.PositiveSmallIntegerField(default=1)
    furnished = models.BooleanField(default=False)
    has_wifi = models.BooleanField(default=True)
    utilities_included = models.BooleanField(default=False)
    lease_duration_months = models.PositiveSmallIntegerField(default=12)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    proximity_to_campus = models.FloatField(
        help_text="Distance to campus in kilometers", default=1.0
    )
    max_occupants = models.PositiveSmallIntegerField(default=4)
    available_from = models.DateField(default=timezone.now)
    security_features = models.JSONField(
        default=dict,
        help_text="e.g. {'gated': True, 'guards': True, 'cctv': False}"
    )
    video = models.FileField(upload_to="house_videos/")
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.title} ({self.location})"


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the URL to access the house's detail page."""
        return reverse("housing:house-detail", kwargs={"pk": self.pk})

    def get_display_name(self):
        return self.title.upper()


class HouseImage(models.Model):
    """
    Images associated with a house listing.

    Fields:
    - house: The related house.
    - image: Actual image file stored in media directory.
    """
    house = models.ForeignKey(House, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="house_images")

class HouseReview(models.Model):
    """
    Review submitted by a user about a house.

    Fields:
    - house: The house being reviewed.
    - author: The user who wrote the review.
    - comment: Textual content of the review.
    - rating: Integer rating (e.g., 1–5).
    - reviewed_on: Timestamp of submission.
    """
    house = models.ForeignKey(House, related_name="reviews", on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.PositiveIntegerField()
    reviewed_on = models.DateTimeField(default=timezone.now)

    def get_absolute_url(self):
        """Redirects to the associated house's detail page."""
        return self.house.get_absolute_url()


class Favorite(models.Model):
    """
    Connects users with houses they’ve favorited.

    Fields:
    - user: The user who favorited the house.
    - house: The house being favorited.
    - favorited_at: Timestamp of favoriting.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    house = models.ForeignKey(House, on_delete=models.CASCADE, related_name="favorites")
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "house")  # Prevent duplicate favorites

    def __str__(self):
        return f"{self.user.username} - {self.house.title} (Favorited on {self.favorited_at})"


