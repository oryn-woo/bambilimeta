from django import forms
from .models import House, HouseImage, HouseReview
from django.forms import modelformset_factory, FileInput


class CreateHouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = "__all__"


HouseImageFormSet = modelformset_factory(  # This essentially creates a set of forms which accept 5 images
    model=HouseImage,
    fields=("image",),
    extra=5,  # Number of empty forms shown
    widgets={
        "image": FileInput()  # FileInput because individual file fields.
    }
)


class HouseReviewForm(forms.ModelForm):
    class Meta:
        model = HouseReview
        fields = ["rating", "comment", "reviewed_on"]
