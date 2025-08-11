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
    RATING_CHOICES = [
        (5, '5 - Excellent'),
        (4, '4 - Very Good'),
        (3, '3 - Average'),
        (2, '2 - Poor'),
        (1, '1 - Terrible'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select bg-dark text-light',
            'required': True
        })
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control bg-dark text-light',
            'rows': 3,
            'required': True,
            'placeholder': 'Write your review here...'
        })
    )
    
    class Meta:
        model = HouseReview
        fields = ["rating", "comment"]
