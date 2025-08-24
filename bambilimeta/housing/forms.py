from django import forms
from .models import House, HouseImage, HouseReview
from django.forms import modelformset_factory, FileInput, inlineformset_factory


from django import forms
from .models import House, HouseImage

class HouseForm(forms.ModelForm):
    class Meta:
        model = House
        fields = ['title', 'location', 'price', 'house_desc', 'video']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a catchy title'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Bambili, close to main market.'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '$ per Month '
            }),
            'house_desc': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Detailed description'
            }),
            'video': forms.FileInput(attrs={
                'class': 'form-control-lg',
                'placeholder': 'Video tour URL'
            }),
        }
        help_texts = {
            'title': 'Keep it short, descriptive, and unique.',
            'location': 'Where is the property located?',
            'price': 'Set a competitive price per night.',
            'house_desc': 'Highlight amenities, space, and nearby attractions.',
            'video': 'Paste a YouTube or Vimeo link for a video tour.',
        }

# Apply Bootstrap’s file‐input class to each image form in the set

HouseImageFormSet = inlineformset_factory(
    House, HouseImage,
    fields=("image",),
    extra=4,
    
    can_delete=True,
    widgets={
        'image': forms.ClearableFileInput(attrs={
            'class': 'form-control form-control-file'
        })
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
