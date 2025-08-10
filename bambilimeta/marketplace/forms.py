from django import forms
from django.forms import modelformset_factory, FileInput, inlineformset_factory
from .models import Product, ProductImage


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = "__all__"


# product_image_formset = modelformset_factory(
#     model=ProductImage,
#     fields=("image",),
#     extra=4,
#     widgets={
#         "image": FileInput(),
#     }
# )

# This method ties images directly to parent product

ImageInlineFormset = inlineformset_factory(
    Product,
    ProductImage,
    fields=("image",),
    extra=4,
    widgets={"image": FileInput(),}
)