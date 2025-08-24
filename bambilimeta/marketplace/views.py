from django.shortcuts import render, redirect
from .models import Product, ProductImage
from .forms import ImageInlineFormset, ProductForm
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Product, Favorite

from django.shortcuts import get_object_or_404, redirect

# class ImageFormsetMixin(BaseFormView):
#     """
#     🧤 A reusable mixin for handling image formsets tied to a parent model instance.
#     Think of it as a butler who knows how to manage the gallery room—whether it’s
#     a house, product, or any other exhibit with multiple images.

#     To use this mixin:
#     - Set `form_class` to your inline formset factory (e.g., HouseImageFormSet)
#     - Set `model` to the parent model (e.g., House)
#     - Set `template_name` to your image upload template
#     - Expect `pk` or `product_id` or `house_id` in `kwargs` (customizable)
#     """

#     model = None  # e.g., House or Product
#     form_class = None  # e.g., HouseImageFormSet
#     template_name = None  # e.g., "housing/house_image_upload.html"
#     context_object_name = "object"  # default name for parent instance
#     pk_url_kwarg = "pk"  # override if using 'house_id' or 'product_id'

#     def dispatch(self, request, *args, **kwargs):
#         """
#         🛎️ Greets the guest and fetches the exhibit (parent model instance).
#         Like a concierge checking the reservation before showing the gallery.
#         """
#         self.object = get_object_or_404(self.model, pk=kwargs.get(self.pk_url_kwarg))
#         return super().dispatch(request, *args, **kwargs)

#     def get_form(self):
#         """
#         🎨 Prepares the formset for editing.
#         Like laying out blank canvases or retouching existing paintings.
#         """
#         if self.request.method == "POST":
#             return self.form_class(
#                 data=self.request.POST,
#                 files=self.request.FILES,
#                 instance=self.object
#             )
#         return self.form_class(instance=self.object)
    
#     def get_form_kwargs(self):
#         kwargs = super().get_form_kwargs()
#         kwargs["instance"] = self.get_object()
#         return kwargs
#     def form_valid(self, formset):
#         """
#         ✅ Saves the formset and redirects.
#         Like approving the artwork and opening the gallery to visitors.
#         """
#         formset.save()
#         return redirect(self.get_success_url())

#     def form_invalid(self, formset):
#         """
#         ❌ Handles validation errors.
#         Like sending the artwork back for touch-ups before the exhibit opens.
#         """
#         return self.render_to_response(self.get_context_data(formset=formset))

#     def post(self, request, *args, **kwargs):
#         """
#         📦 Handles POST requests.
#         Like sorting incoming packages—some go to display, others back to sender.
#         is_valid is built in and will chech that all individaul 
#         forms in the formset is valid. It cas be managed by subclassing the 
#         formset and overriding the clean() validation logic.
        
#         """
#         formset = self.get_form()
#         if formset.is_valid():
#             return self.form_valid(formset)
#         return self.form_invalid(formset)

#     def get_context_data(self, **kwargs):
#         """
#         🧠 Prepares the template context.
#         Like setting the stage with props and lighting before the curtain rises.
#         """
#         context = super().get_context_data(**kwargs)
#         context["formset"] = kwargs.get("formset", self.get_form())
#         # This if formset is already passed in kwargs from form_valid(), it uses it
#         # Otherwise it calls self.get_form() to generate a fresh formset
#         context[self.context_object_name] = self.object
#         return context

#     def get_success_url(self):
#         """
#         🔁 Defines where to go after saving.
#         Override this in your subclass to redirect to the appropriate detail page.
#         This exception is raised only if you dont provide a success url
#         """
#         raise NotImplementedError("You must define get_success_url() in your subclass.")


     



# class ProductCreateView(View):
#     """
#     A raw view is used to handle HTTP request.
#     This class is designed to identify and map methods to their
#     corresponding HTTP request types."""
#
#
#
#     def get(self, request, *args, **kwargs):
#         """
#         A get request renders the form.
#         :param request: Request object
#         :return: Template and context.
#         """
#         form = ProductForm()
#         formset = ImageInlineFormset(queryset=ProductImage.objects.none())
#         return render(request, "marketplace/product_form.html", {"formset": formset, "form": form})
#
#     def post(self, request, *args, **kwargs):
#         form = ProductForm(request.POST)
#         formset = ImageInlineFormset(
#             request.POST, request.FILES, queryset=ProductImage.objects.none(),
#         )
#
#         if form.is_valid() and formset.is_valid():
#             product = form.save()
#             images = formset.save(commit=False)
#             for img in images:
#                 img.product = product
#                 img.save()
#             return redirect(product.get_absolute_url())
#         return render(request, "marketplace/product_form.html", {"formset": formset, "form": form})

@method_decorator(login_required, name="dispatch")
class ProductCreateView(CreateView):
    """
    <<<//--Read commented Product ProductCreateView(View)-->>> This signal is about reading commented code above (//)
    FormView is designed to handle a single form only. So we can use the View and manaully validate our form in post() and get()
    Or Use CreateView + FormMixin + InlineFormSet
    Thus view
    Handles creation of a Product along with its related images
    using a main ProductForm and an ImageInlineFormset.

    This class extends Django's built-in CrearteView but overrides context and saving logic
    to support multiple forms.
    Flow
    - GET: Display a blank ProductForm and empty ImageInlineFormset.
    - POST: Validate both ProductForm ImageInlineFormset
    - If valid: save Product, attach product to each image, save images.
    - If invalid: re-render the form with validation errors.
    - get_context_data is called after the form_class has already bound the form_class (ProductForm)
    - so our form is now available in context as context['form']
    - So django builds main form (ProductForm) via get_form() then calls get_context_data(form=form, ...)
        where extra content is injected like formset. Finally renders the template on GET or continues validation on POST
        get_context_data is a transition stage where we enrich the template either empty formset (GET) or
        bound formset (POST)

    """
    model = Product
    form_class = ProductForm
    template_name = "marketplace/product_form.html"

    def get_context_data(self, **kwargs):
        """
        Inject both the main form and the formset into the template context
        - On GET request: provide empty ProductForm and ImageInlineFormset.
        - On POST request: bind submitted data/files to both.
        :param kwargs: Other kwargs
        :return: The context
        """
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            # Bind POST data to both form and formset
            context["formset"] = ImageInlineFormset(self.request.POST, self.request.FILES, queryset=ProductImage.objects.none())
        else:
            # Empty formset when initially rendering page
            context["formset"] = ImageInlineFormset(queryset=ProductImage.objects.none())
        return context

    def form_valid(self, form):
        """
        Custom save logic for handling both the product and images.
        Steps
        1. Validate the formset
        2. if valid, save the Product (via the main form )
        3. Save each image from the formset, attaching it to the Product.
        4. Redirect to the Product detail page (get_absolute_url).
        :param form:  The form object
        :return: form with errors or redirect page
        """
        context = self.get_context_data()
        formset = context["formset"]
        if formset.is_valid():
            # self.object = form.save(commit=False)  # Save the actual product form in memory not db
            # self.object.seller = self.request.user  # Assign current logged in user as seller.
            # self.object.save()  # Product now saved with id  for user
            # # Save the formset images with product attached
            # images = formset.save(commit=False)
            # for img in images:
            #     img.product = self.object
            #     img.save()

            # Delete any extra images marked for deletion
            #  <<<//--Read commented Product form saving logic-->>>
            # create product instance and save to the memory
            product = form.save(commit=False)
            # Assign currently login user as seller
            product.seller = self.request.user

            # Now save product to database with current user. It now has ID
            product.save()

            # Set the instance for the formset to our newly created product

            # This links images to correct product
            formset.instance = product
            formset.save()  # This saves all images correctly

            # Store the created product instance to be used by get_success_url
            self.object = product

            # Redirect to product details page
            return redirect(self.object.get_absolute_url())
        else:
            # If formset is not valid re-render with form and formset erros.

            return self.form_invalid(form)


class ProductListView(ListView):
    """
    A view to list all products.
    """
    model = Product
    template_name = "marketplace/product_list.html"
    context_object_name = "products"
    # Good practice to add a success url

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Get the context for the home page.

        :param object_list: The list of objects to be displayed
        :param kwargs: Additional keyword arguments
        :return: The context for the home page
        """
        context = super().get_context_data(**kwargs)
        # If the request was made from the home page, show the hero section
        from_home = self.request.GET.get("from") == "home"
        context["show_hero"] = from_home
        # Get the first product as the hero product
        context["hero_product"] = Product.objects.first()
        return context


class ProductDetailView(DetailView):
    model = Product
    context_object_name = "product"
    template_name = "marketplace/product_detail.html"


def toggle_favorite(request, pk):

    # expects POST
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=400)

    product = get_object_or_404(Product, pk=pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        # already existed -> unfavorite
        fav.delete()
        favorited = False
    else:
        favorited = True

    return JsonResponse({'favorited': favorited})


# class ProductUpdateView(UpdateView):
#     model = Product
#     form_class = ProductForm




# class ProductUpdateView(LoginRequiredMixin, UpdateView):
#     """
#     View to update a Product and its related ProductImage entries.
#     Handles:
#       - Displaying existing images
#       - Adding new images
#       - Deleting checked images
#     """
#     model = Product
#     form_class = ProductForm
#     template_name = "marketplace/product_update.html"
#     success_url = reverse_lazy("marketplace:product-list")

#     # def test_func(self):
#     #     """
#     #     Ensure that only the product owner can edit this product.
#     #     Adjust logic as needed (e.g., staff users).
#     #     """
#     #     product = self.get_object()
#     #     return product.seller == self.request.user

#     def get_context_data(self, **kwargs):
#         """
#         Insert the ImageInlineFormset into the context.
#         If POST data is present, bind it to capture uploads/deletions.
#         """
#         context = super().get_context_data(**kwargs)
#         if self.request.method == "POST":
#             context["formset"] = ImageInlineFormset(
#                 self.request.POST,
#                 self.request.FILES,
#                 instance=self.object,
#             )
#         else:
#             context["formset"] = ImageInlineFormset(instance=self.object)
#         return context

#     def form_valid(self, form):
#         """
#         Called when the main ProductForm is valid.
#         We must also validate and save the formset before final redirect.
#         """
#         context = self.get_context_data()
#         formset = context["formset"]
#         # Save the Product instance first
#         self.object = form.save()

#         if formset.is_valid():
#             # Link formset to the saved product and commit changes
#             formset.instance = self.object
#             formset.save()
#         else:
#             # If formset has errors, re-render the page with error messages
#             return self.form_invalid(form)

#         return super().form_valid(form)

#
# def product_image_edit(request, product_id):
#     # Get the house model or return 404
#     product = get_object_or_404(Product, id=product_id)
#
#     # Create a formset instance
#     formset = ImageInlineFormset(instance=product)
#
#     if request.method == "POST":
#         # Bind the formset to the post data
#         formset = ImageInlineFormset(
#             request.POST, request.FILES,  instance=product
#         )
#         if formset.is_valid():
#             formset.save()  # Save the formset
#             return redirect("market:product-detail", pk=product.id)
#     return render(request, "marketplace/product_image_upload.html", {"formset": formset, "product": product})
#

# class ProductImageEditView(BaseFormView):
#     """
#     🎩 A refined butler-style view that handles image editing for a specific Product.
#     It uses a formset to manage multiple related Image objects tied to one Product.
#     Think of it as a concierge managing a gallery of paintings for a single exhibit.
#     """
#
#     template_name = "marketplace/product_image_upload.html"
#     form_class = ImageInlineFormset
#
#     def dispatch(self, request, *args, **kwargs):
#         """
#         🛎️ The grand entrance. This method is called first and decides which door to open:
#         GET or POST. Before doing so, it fetches the Product instance like a host
#         checking the guest list before letting anyone in.
#
#         Metaphor: Imagine a maître d’ at a restaurant who checks your reservation
#         before showing you to your table. If your name isn’t on the list, you’re not getting in.
#         """
#
#         self.product = get_object_or_404(Product, id=self.kwargs["product_id"])
#         return super().dispatch(request, *args, **kwargs)
#
#     def get_form(self):
#         """
#         🧰 Prepares the formset for use. If it's a POST request, it loads submitted data;
#         otherwise, it prepares a blank canvas tied to the product.
#
#         Metaphor: Like a painter choosing between a fresh canvas or retouching an existing one.
#         """
#         if self.request.method == "POST":
#             return self.form_class(
#                 data=self.request.POST,
#                 files=self.request.FILES,
#                 instance=self.product
#             )
#         return self.form_class(instance=self.product)
#
#     def form_valid(self, formset):
#         """
#         ✅ Called when the formset passes validation. Saves the images and redirects.
#
#         Metaphor: Like a curator approving all paintings for an exhibit and opening the gallery doors.
#         """
#         formset.save()
#         return redirect("market:product-detail", pk=self.product.id)
#
#     def form_invalid(self, formset):
#         """
#         ❌ Called when the formset fails validation. Renders the form again with errors.
#
#         Metaphor: Like a quality inspector rejecting a batch and sending it back for rework.
#         """
#         return self.render_to_response(self.get_context_data(formset=formset))
#
#     def post(self, request, *args, **kwargs):
#         """
#         📦 Handles POST requests. Validates the formset and routes to the appropriate handler.
#
#         Metaphor: Like a mailroom sorting incoming packages—some go to delivery, others back to sender.
#         """
#         formset = self.get_form()
#         if formset.is_valid():
#             return self.form_valid(formset)
#         return self.form_invalid(formset)
#
#     def get_context_data(self, **kwargs):
#         """
#         🧠 Supplies the template with context variables: the formset and product.
#
#         Metaphor: Like a stage manager laying out props and scripts before the curtain rises.
#         """
#         context = super().get_context_data(**kwargs)
#         context["formset"] = kwargs.get("formset", self.get_form())
#         context["product"] = self.product
#         return context


# class ProductImageEditView(View):
#     """
#     A Class‐Based View version of the function “product_image_edit”.
#     It handles display and processing of the ImageInlineFormset for one Product.
#     Think of it as a gallery curator who, on GET, lays out all the paintings (images),
#     and on POST, reviews submitted updates before hanging them back on the wall.
#     """
#
#     model = Product
#     formset_class = ImageInlineFormset
#     template_name = "marketplace/product_image_upload.html"
#     pk_url_kwarg = "product_id"
#
#     def get(self, request, *args, **kwargs):
#         """
#         Handle GET requests:
#         - Fetch the product.
#         - Instantiate an unbound formset with existing images.
#         - Render the template with that formset.
#
#         Metaphor: The curator unlocks the gallery, arranges the existing paintings,
#         and invites the visitor in to view them.
#         """
#         product = self.get_object()
#         formset = self.formset_class(instance=product)
#         return render(request, self.template_name, self.get_context_data(product, formset))
#
#     def post(self, request, *args, **kwargs):
#         """
#         Handle POST requests:
#         - Fetch the product.
#         - Bind the formset to POST data + files.
#         - If valid, save and redirect to detail.
#         - If invalid, re‐render with errors.
#
#         Metaphor: The curator inspects the new or edited paintings. If they pass,
#         they’re hung in the gallery; otherwise they’re sent back to the artist for touch-ups.
#         """
#         product = self.get_object()
#         formset = self.formset_class(request.POST, request.FILES, instance=product)
#
#         if formset.is_valid():
#             formset.save()
#             return redirect("market:product-detail", pk=product.id)
#
#         return render(request, self.template_name, self.get_context_data(product, formset))
#
#     def get_object(self):
#         """
#         Look up and return the Product instance based on URL kwargs.
#         Raises 404 if not found.
#
#         Metaphor: Checking the guest list (product_id) before letting someone into the gallery.
#         """
#         return get_object_or_404(self.model, id=self.kwargs.get(self.pk_url_kwarg))
#
#     def get_context_data(self, product, formset):
#         """
#         Build the context dict for rendering.
#
#         Metaphor: Laying out the visitor’s guide (product info) and the wall labels (formset)
#         before they enter the gallery.
#         """
#         return {
#             "product": product,
#             "formset": formset,
#         }

class InlineFormsetEditView(View):

    model = None
    form_class = None
    template_name = None
    pk_url_kwarg = None
    success_url = None

    def get_object(self):
        """
        Get the instance of the parent class whom we will use as instance for formset
        :return: The object or a 404 if not found
        """
        return get_object_or_404(self.model, id=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, object, formset):
        """
        Dynamically builds context using the model name as key.
        Example: {"product": object, "formset": formset}
        """
        model_key = self.model.__name__.lower()
        return {
            model_key: object,
            "formset": formset,
        }

    def get(self, request, *args, **kwargs):
        """
        A get request, which help prepopulate the form with the instance we (get_object)
        :return: a response
        """
        object = self.get_object()
        formset = self.form_class(instance=object)
        return render(request, self.template_name, self.get_context_data(object, formset))  # passed as position arguments

    def form_invalid(self, formset, object):
        return render(self.request, self.template_name, self.get_context_data(object, formset))
    def post(self, request, *args, **kwargs):
        """
        Validates the submitted form and updates database.
        :param request: Request object
        :param args: Other args
        :param kwargs: Other kwargs
        :return: A response or redirect
        """
        object = self.get_object()  # if we add
        formset = self.form_class(request.POST, request.FILES, instance=object)

        if formset.is_valid():
            formset.save()
            return redirect(object.get_absolute_url() if hasattr(object, "get_absolute_url") else self.success_url)

        return self.form_invalid(object, formset)

class ProductImageEditView(InlineFormsetEditView):
    """
    A subclass of InlineFormsetEditView tailored for editing images of a Product.
    Think of it as a gallery curator who uses a reusable framework to manage paintings.
    """

    model = Product
    form_class = ImageInlineFormset
    template_name = "marketplace/product_image_upload.html"
    pk_url_kwarg = "product_id"
    success_url = None  # Optional: fallback if get_absolute_url isn't defined

    def get_context_data(self, object, formset):
        return {
            "product": object,
            "formset": formset
        }


def product_details_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            # product.seller = request.user : Not needed we are editing
            form.save()
            return redirect("market:product-detail", pk=product.id)
        else:
            return render(request, "marketplace/product_details_edit.html", {"form": form, "product": product})
    return render(request, "marketplace/product_details_edit.html", {"form": ProductForm(instance=product), "product": product})


class ProductDetailsUpdateView(UpdateView):
    model = Product
    template_name = "marketplace/product_details_edit.html"
    form_class = ProductForm
    pk_url_kwarg = "product_id"

    def get_success_url(self):
        return self.object.get_absolute_url()
