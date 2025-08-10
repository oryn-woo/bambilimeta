from django.shortcuts import render, redirect
from .models import Product, ProductImage
from .forms import ImageInlineFormset, ProductForm
from django.views.generic import View, ListView, DetailView


class ProductCreateView(View):
    """
    A raw view is used to handle HTTP request.
    This class is designed to identify and map methods to their
    corresponding HTTP request types."""

    def get(self, request, *args, **kwargs):
        """
        A get request renders the form.
        :param request: Request object
        :return: Template and context.
        """
        form = ProductForm()
        formset = ImageInlineFormset(queryset=ProductImage.objects.none())
        return render(request, "marketplace/product_form.html", {"formset": formset, "form": form})

    def post(self, request, *args, **kwargs):
        form = ProductForm(request.POST)
        formset = ImageInlineFormset(
            request.POST, request.FILES, queryset=ProductImage.objects.none(),
        )

        if form.is_valid() and formset.is_valid():
            product = form.save()
            images = formset.save(commit=False)
            for img in images:
                img.product = product
                img.save()
            return redirect(product.get_absolute_url())
        return render(request, "marketplace/product_form.html", {"formset": formset, "form": form})


class ProductListView(ListView):
    """
    A view to list all products.
    """
    model = Product
    template_name = "marketplace/wlcm.html"
    context_object_name = "products"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        from_home = self.request.GET.get("from") == "home"
        context["show_hero"] = from_home
        context["hero_product"] = Product.objects.first()
        return context


class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"
    template_name = "marketplace/index.html"
