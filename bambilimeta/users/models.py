from django.db import models
from django.contrib.auth.models import User, AbstractUser
from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django import forms
from django.shortcuts import reverse

class Profile(models.Model):
    """
    Extension of the built-in User model with visual and professional attributes.

    Fields:
    - user: One-to-one link to the User model.
    - image: Profile picture (auto-resizes on save).
    - role: Functional role of the user (landlord, entrepreneur...).
    - phone_number: Optional contact number.
    - bio: Short biography or tagline.
    """

    ROLE_CHOICES = [
        ('regular', 'Regular User'),
        ('landlord', 'Landlord'),
        ('entrepreneur', 'Entrepreneur'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(default="default.jpeg", upload_to="profile_pics")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='regular')
    phone_number = PhoneNumberField(blank=True)
    bio = models.CharField(blank=True, max_length=2000)


    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        """
        Overrides default save behavior.

        Purpose:
        Resizes profile image to max 300x300 pixels
        for consistent display and bandwidth savings.
        """
        super().save(*args, **kwargs)
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_absolute_url(self):
        """
        The reverse method returns the url string. It expect its arguments via kwargs dictionary.
        So essentially we say find the url pattern named auth:profile and fill <int:pk> with self.pk
        :return:
        """
        return reverse("auth:profile", kwargs={"pk": self.pk})