from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class UserUpdateForm(forms.ModelForm):
    """Update username and email."""
    class Meta:
        model = User
        fields = ["username", "email"]


class ProfileUpdateForm(forms.ModelForm):
    """Update profile image, bio, phone number."""
    class Meta:
        model = Profile
        fields = ["image", "bio", "phone_number"]
        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 10, "cols": 10
            }),

        }


class AdminProfileUpdateForm(ProfileUpdateForm):
    """Update profile incl. role (for admin use)."""
    class Meta(ProfileUpdateForm.Meta):
        fields = ["image", "phone_number", "bio", "role"]
        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 10, "cols": 10
            }),
            "role": forms.Select(attrs={
                "class": "form-select"
            }),
            "image": forms.FileInput(attrs={
                "class": "form-control"
            })
        }


# class ProfileForm(forms.ModelForm):
#     class Meta:
#         model = Profile
#         fields = ["image", "role", "phone_number", "bio"]
#         widgets = {
#             "role": forms.Select(attrs={
#                 "class": "form-control"
#             }),
#             "phone_number": forms.TextInput(attrs={
#                 "class": "form-control"
#             }),
#             "bio": forms.Textarea(attrs={
#                 "class": "form-control", "rows": 4
#             }),
#             "image": forms.ClearableFileInput(attrs={
#                 "class": "form-control-file"
#             })
#         }