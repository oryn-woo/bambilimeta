from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    """
    This form updates a particular model in the database, in this case the user model.
    Will update their username and email.
    """

    class Meta:
        model = User
        fields = ["username", "email"]


class ProfileUpdateForm(forms.ModelForm):
    """
    This form allows us to update image.
    """
    class Meta:
        model = Profile
        fields = ["image", "bio", "phone_number"]


class AdminProfileUpdateForm(ProfileUpdateForm):
    """
    Created to add a layer of security when managing regular users and admins.
    """
    class Meta(ProfileUpdateForm.Meta):
        fields = ["image", "phone_number", "bio", "role"]
