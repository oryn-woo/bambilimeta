from django import forms
from django.forms import modelformset_factory, FileInput, inlineformset_factory
from .models import Product, ProductImage


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ["name", "price", "stock", "description", "stock"]



# This method ties images directly to parent product
ImageInlineFormset = inlineformset_factory(
    Product,
    ProductImage,
    fields=("image",),
    can_delete=True,
    extra=2,
    widgets={
      "image": FileInput(attrs={"class": "form-control"})
    },
)