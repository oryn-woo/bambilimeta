from django.db import models
from django.contrib.auth.models import User, AbstractUser
from PIL import Image
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django import forms


class Profile(models.Model):
    """
    Extends the built-in User model with a profile image.
    Automatically resizes the image to a maximum of 300x300 pixels upon saving.
    """
    ROLE_CHOICES = [
        ('regular', 'Regular User'),
        ('landlord', 'Landlord'),
        ('entrepreneur', 'Entrepreneur'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="default.jpeg", upload_to="profile_pics")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='regular')
    phone_number = PhoneNumberField(blank=True)
    bio = models.CharField(blank=True, max_length=2000)

    def __str__(self):
            return self.user.username




    def save(self, *args, **kwargs):
        """
        Overrides the default save method to resize the profile image
        if its dimensions exceed 300x300 pixels.

        Parameters:
        - *args: Variable length argument list passed to the original save method.
        - **kwargs: Arbitrary keyword arguments passed to the original save method.
        """
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
