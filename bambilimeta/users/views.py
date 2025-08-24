from django.shortcuts import render, redirect, reverse
from django.views.generic import DetailView, FormView
from django.contrib import messages
from .forms import UserUpdateForm, UserRegisterForm, AdminProfileUpdateForm
from marketplace.models import Product
from housing.models import House, Favorite
from .models import Profile
from django.db.models import Prefetch, Exists, OuterRef
from itertools import chain
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy


# class Register(View):
#     def get(self, request, *args, **kwargs):
#         form = UserRegisterForm()
#         return render(request, "users/register.html", context={"form": form})
#
#     def post(self, request, *args, **kwargs):
#         form = UserRegisterForm(request.POST)
#         if form.is_valid():
#             new_user = form.save()
#             username = form.cleaned_data.get("username")
#             messages.success(request, message="Account created successful")
#             return redirect("auth:profile", kwargs={"pk":new_user.id})
#         return render(request, "users/register.html", context={"form": form})



# @login_required
# def profile(request):
#     profile = request.user.profile
#     FormClass = AdminProfileUpdateForm if request.user.is_staff or request.user.profile.role != 'regular' else ProfileUpdateForm
#
#     if request.method == "POST":
#         # Copy POSt so fields can be safely removed (prevent tampering)
#         post = request.POST.copy()
#         # If user is regular, remove any role included in POST
#         if profile.role == "regular":
#             post.pop("role", None)
#         u_form = UserUpdateForm(request.POST, instance=request.user)
#         p_form = FormClass(post, request.FILES, instance=profile)
#         # The image uploaded by user.
#
#
#         if u_form.is_valid() and p_form.is_valid():
#             # final enforcement: ensure regular user cannot escalate role
#             if request.user.profile.role == "regular":
#                 p_form.instance.role = request.user.profile.role
#             u_form.save()
#             p_form.save()
#             messages.success(request, message="Your account has been updated!.")
#             return redirect("auth:profile")
#
#     else:
#         u_form = UserUpdateForm(instance=request.user)
#         p_form = ProfileUpdateForm(instance=profile)
#
#     # helpful flag for template: whether the 'role' field exists (so template shows it)
#     show_role = 'role' in p_form.fields
#
#     context = {
#         "u_form": u_form,
#         "p_form": p_form,
#         "products": Product.objects.all(),
#         "show_role": show_role
#     }
#     return render(request, "users/profile.html", context)

# class SmartFromSuccessMixin:
#     """
#     A reusable mixin for django form views that
#     - Saves the form and returns the redirect response.
#     - Adds customizable success messages
#     - supports dynamic redirect URLs via get_success_url()
#     - Allows injection of rich HTML links via get_success_link()
#     """
#     success_message = None  # Plain  success message
#     success_links = []  # List of (label, url_name) tuple

#     def form_valid(self, form):
#         # Save the form and get the redirect response
#         response = super().form_valid(form)
#         # Add succes message if defined.
#         if self.success_message:
#             messages.success(self.request, self.success_message)

#         # Add additional info message with links
#         for label, url_name in self.get_success_links():
#             try:
#                 url = reverse_lazy(url_name)
#                 html = f"<a href='{url}' class='btn btn-sm btn-primary'>{label}</a>"
#                 messages.success(self.request, mark_safe(html))
#             except Exception as e:
#                 messages.warning(self.request, f"Could not generate link for {label}, : {e}")
#         return response
#     def get_success_links(self):
#         """
#         Override this to return a list of (label, url_name)
#         Example: [('Go to Dashboard', 'dashboard'), ('View Profile')
#         :return: List of links
#         """
#         return self.success_links

from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe


class SmartFormSuccessMixin:
    """
    A reusable mixin for Django form views that:
    - Handles saving/login and redirects via form_valid().
    - Adds customizable success messages.
    - Supports dynamic redirect URLs via get_success_url().
    - Allows injection of rich HTML links via get_success_links().
    - Optionally supports 'remember me' session expiry control.
    - Provides a safe form_invalid() handler.
    """

    success_message = None         # Plain success message
    success_links = []             # List of (label, url_name) tuples
    remember_me_field = "remember" # Name of the remember-me checkbox input

    def form_valid(self, form):
        """
        Called when the submitted form is valid.
        Runs parent logic (saves/login), then adds messages & remember-me handling.
        """
        # Let parent handle saving / login
        response = super().form_valid(form)

        # ✅ Handle 'Remember Me'
        self.apply_remember_me()

        # ✅ Add success message if defined
        if self.success_message:
            messages.success(self.request, self.success_message)

        # ✅ Add additional info messages with links
        for label, url_name in self.get_success_links():
            try:
                url = reverse_lazy(url_name)
                html = f"<a href='{url}' class='btn btn-sm btn-primary'>{label}</a>"
                messages.info(self.request, mark_safe(html))
            except Exception as e:
                messages.warning(self.request, f"Could not generate link for {label}: {e}")

        return response

    def form_invalid(self, form):
        """
        Called when the submitted form is invalid.
        Ensures the form + errors are rendered properly.
        """
        return self.render_to_response(self.get_context_data(form=form))

    
    # 🔹 Utility custom methods

    def apply_remember_me(self):
        """
        Handles session expiry if a 'remember me' field is posted.
        Default: 2 weeks if checked, else expire on browser close.
        """
        if self.remember_me_field in self.request.POST:
            remember = self.request.POST.get(self.remember_me_field)
            if remember:
                self.request.session.set_expiry(1209600)  # 2 weeks
            else:
                self.request.session.set_expiry(0)        # Browser close

    def get_success_links(self):
        """
        Override this to return a list of (label, url_name).
        Example: [('Go to Dashboard', 'dashboard'), ('View Profile', 'profile')]
        """
        return self.success_links



class RegisterView(FormView):
    """
    Handles user registration using Django's FormView.
    Automatically renders the form on GET and re-renders with errors on invalid POST.
    """

    template_name = "users/register.html"  # Template to render
    form_class = UserRegisterForm          # Form to use


    # def form_valid(self, form):
    #     """
    #     Called when submitted form is valid.
    #     Saves the user, shows a success message, and redirects to profile.
    #     We use redirect here because it depends on runtime data, which is dynamic.
    #     Notes
    #     - Here we manually save the form.save()
    #     - Manually trigger a success message with messages.success.
    #     - Manually redirect using redirect
    #     - This works but bypasses django's built in flow, an introduces subtle risk.
    #     """
    #     new_user = form.save()
    #     messages.success(self.request, "Account created successfully")
    #
    #     # Redirect to profile using dynamic user ID
    #     # return redirect("auth:profile", kwargs={"pk": new_user.id}) this lines give an error, redirect requires pk directly as kwarg i.e.
    #     return redirect("auth:profile", pk=new_user.id)
    def form_valid(self, form):
        """
        <<<//--Read commented form_valid_above-->>> This signal is about reading commented code above (//)
        Here the super().form_valid(form) saves the form
        - sets self.object to the newly created user.
        - handles session updates and signals.
        - This aligns with get success url which resolves redirect
        - It calls the get_success_url() to determine where to redirect
        - This keeps code modular and testable.
        - Returns an HttpResponseRedirect to the success URL.
        :param form: The form object
        :return: The response. The response is not the saved object
         it's the actual redirect response that django sends to the browser
         django expects a valid HTTP response from our view method.
        """
        self.object = form.save()
        messages.success(self.request, "Account created successful")
        return super().form_valid(form)

    def get_success_url(self):
        """
        Overriding the success url for dynamic redirects after the form is valid and save and our self.object is available.
        :return: The url string
        """
        # return reverse("auth:profile", kwargs={"pk": self.object.pk})
        return reverse("auth:login")

    def form_invalid(self, form):
        """
        Called when submitted form is invalid.
        Re-renders the form with validation errors.
        """
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        """
        Adds extra context to the template.
        You can inject tooltips, icons, or partials here later.
        """
        context = super().get_context_data(**kwargs)
        context["title"] = "Create Your Account"
        # Example: context["tooltip_text"] = "Your username must be unique"
        return context



class ProfileView(DetailView):
    """
    Shows a user's profile with their products and houses,
    and allows the profile owner (or staff) to edit User + Profile info.
    """
    model = Profile
    template_name = "users/profile.html"
    context_object_name = "user_profile"

    def get_queryset(self):
        viewer = self.request.user if self.request.user.is_authenticated else None

        product_qs = Product.objects.prefetch_related("images")
        house_qs = House.objects.prefetch_related("images", "reviews")

        if viewer:
            house_qs = house_qs.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user_id=viewer.pk, house_id=OuterRef("pk"))
                )
            )

        return (
            Profile.objects
            .select_related("user")
            .prefetch_related(
                Prefetch("user__products", queryset=product_qs),
                Prefetch("user__houses", queryset=house_qs),
            )
        )

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        context["profile_owner"] = self.object.user

        # if owner or staff → add forms
        if request.user.is_authenticated and (
            request.user == self.object.user  # or request.user.is_staff
        ):
            context["user_form"] = UserUpdateForm(instance=self.object.user)
            context["profile_form"] = AdminProfileUpdateForm(instance=self.object)

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Security check
        if not request.user.is_authenticated or request.user != self.object.user:
            return redirect(self.object.get_absolute_url())

        user_form = UserUpdateForm(request.POST, instance=self.object.user)
        profile_form = AdminProfileUpdateForm(
            request.POST, request.FILES, instance=self.object
        )

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            previous_url = request.META.get("HTTP_REFERER")
            return redirect(previous_url or self.object.get_absolute_url())

        # Re-render with errors
        context = self.get_context_data(
            user_form=user_form,
            profile_form=profile_form
        )
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Portfolio items (products + houses)
        u = self.object.user
        products = list(u.products.all())
        houses = list(u.houses.all())
        merged = list(chain(products, houses))
        merged.sort(
            key=lambda x: getattr(x, "created_at", None)
                        or getattr(x, "updated_at", None),
            reverse=True
        )

        context["products"] = products
        context["houses"] = houses
        context["portfolio_items"] = merged

        # Allow pre-passed forms (from get/post)
        if "user_form" not in context:
            context["user_form"] = None
        if "profile_form" not in context:
            context["profile_form"] = None

        return context


class CustomLoginView(SmartFormSuccessMixin, LoginView):
    """
    Override to gain some control over functioning
    When i first inherit from my mixin, django builds a MRO (method resolution order. a chain django uses to look up methods and attributes)
    More pricise MRO oder here is 
    [CustomLoginView --> SmartFormSuccessMixin --> LoginView --> Base Classes --> object]
     > When django calls form_valid python first check CustomLoginView has the method if not, it moves to SmartFormSuccessMixin.
     > But inside we called super().form_valid() so python jumps to the next class in the MRO, which is LoginView.form_valid 
    So if in this view i provide a success_message, my Mixins default will be overriden
    """
    template_name = "users/login.html"
    success_url = reverse_lazy("market:products")
    success_message = "Welcome to Bambili Housing & E-commerce!"

    def get_success_links(self):
        # return super().get_success_links()
        return [
            ("visit Market", "market:products"),
            ("Visit Houses", "housing:house-list"),
        ]

    # def form_valid(self, form):
    #     # This method is called after a successful login
    #     # A this stage the user is not yet login into the request object,
    #     # so we call the parent method first to perform the login
    #     response = super().form_valid(form)
    #     # Now the user is logged in and available via self.request.user.
    #     # Now we can access their user name and render a proper response

    #     # handle remeber me
    #     remember_me = self.request.POST.get("remember", None)
    #     if remember_me:
    #         # Persitent 2 weeks.
    #         self.request.session.set_expiry(1209600)
    #     else:
    #         # session expires when browser closses.
    #         self.request.session.set_expiry(0)

    #     market_url = reverse("market:products")
    #     house_url = reverse("housing:house-list")
    #     market_link = f"Visit our houses <a href='{market_url}' class='btn btn-primary btn-sm'>market</a>"
    #     house_link = f"Visit our houses <a href='{house_url}' class='btn btn-primary btn-sm'>Houses</a>"

    #     messages.success(self.request, f"Welcome {self.request.user.username} to bambili housing and eCommerce.")
    #     messages.info(self.request, message=mark_safe(market_link))
    #     messages.info(self.request, message=mark_safe(house_link))


    #     # Return the response from the parent object usually a redirect.
    #     return response

    # def form_invalid(self, form):
    #     return self.render_to_response(self.get_context_data(form=form))









# class ProfileView(DetailView):
#     model = Profile
#     template_name = "users/profile.html"
#     context_object_name = "user_profile"
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         profile_user = self.object.user
#
#         # 1. Fetch both lists
#         products = list(profile_user.products.all())
#         houses   = list(profile_user.houses.all())
#
#         # 2. Annotate for unified rendering
#         for p in products:
#             p.display_name = p.name
#             p.url          = p.get_absolute_url()
#             p.price        = p.price
#             p.type_label   = "Product"
#
#         for h in houses:
#             h.display_name = h.title
#             h.url          = h.get_absolute_url()
#             h.price        = h.price
#             h.type_label   = "House"
#
#         # 3. Combine & optionally sort by creation date
#         combined = list(chain(products, houses))
#         combined.sort(key=lambda x: getattr(x, "created_at", None), reverse=True)
#
#         context["portfolio_items"] = combined
#         return context


#
# class ProfileView(DetailView):
#     model = Profile
#     template_name = "users/profile.html"
#     context_object_name = "user_profile"
#
#
#     def get_queryset(self):
#         viewer = self.request.user if self.request.user.is_authenticated else None
#
#         # Example with explicit through model for House favorites.
#         # If you use implicit M2M, swap to House.favorites.through.
#         house_fav_through = House.favorites.through  # adjust if you named it
#
#         product_qs = Product.objects.prefetch_related("images")
#         house_qs = House.objects.prefetch_related("images", "reviews")
#
#         if viewer:
#             house_qs = house_qs.annotate(
#                 is_favorited=Exists(
#                     house_fav_through.objects.filter(
#                         user_id=viewer.pk, house_id=OuterRef("pk")
#                     )
#                 )
#             )
#             # Same idea for products if/when you add that M2M.
#
#         return (
#             Profile.objects.select_related("user").prefetch_related(
#                 Prefetch("user__seller", queryset=product_qs),
#                 Prefetch("user__owner", queryset=house_qs),
#             )
#         )
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["products"] = Product.objects.filter(user=self.user).all()
#         context["houses"] = House.objects.filter(user=self.user).all()
#         return context
#


# class ProfileView(DetailView):
#     """
#     Displays the profile of a user, showcasing their products and properties.
#
#     - Annotates houses with 'is_favorited' if the viewing user has favorited them.
#     - Prefetches associated product and house data efficiently.
#     """
#     model = Profile
#     template_name = "users/profile.html"
#     context_object_name = "user_profile"
#
#     def get_queryset(self):
#         viewer = self.request.user if self.request.user.is_authenticated else None
#
#         # Optimize related queries
#         product_qs = Product.objects.prefetch_related("images")
#         house_qs = House.objects.prefetch_related("images", "reviews")
#
#         # Annotate houses with is_favorited flag
#         if viewer:
#             house_qs = house_qs.annotate(
#                 is_favorited=Exists(
#                     Favorite.objects.filter(user_id=viewer.pk, house_id=OuterRef("pk"))
#                 )
#             )
#
#         return Profile.objects.select_related("user").prefetch_related(
#             Prefetch("user__product_set", queryset=product_qs),
#             Prefetch("user__house_set", queryset=house_qs),
#         )
#
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         user = self.object.user
#
#         products = list(user.product_set.all())
#         houses = list(user.house_set.all())
#
#         # Give each item a common attribute for template rendering
#         for obj in chain(products, houses):
#             obj.display_name = getattr(obj, "name", None) or getattr(obj, "title", "")
#             obj.type_label = obj._meta.model_name  # "product" or "house"
#
#         context["portfolio_items"] = list(chain(products, houses))
#         return context
#
#     # def get_context_data(self, **kwargs):
#     #     context = super().get_context_data(**kwargs)
#     #     profile_user = self.object.user  # Correct way to access the profile's user
#     #
#     #     # context["products"] = Product.objects.filter(seller=profile_user)[:3]
#     #     # context["houses"] = House.objects.filter(owner=profile_user)[:3]
#     #
#     #     user = get_object_or_404(User, id=self.kwargs["pk"])
#     #     context["houses"] = House.objects.filter(owner=user)
#     #     context["products"] = Product.objects.filter(seller=user)
#     #     # context["houses"] = House.objects.all()
#     #     # context["products"] = Product.objects.all()
#     #     # profile_items = list(context["products"]) + list(context["houses"])
#     #     # for obj in profile_items:
#     #     #     obj.display_name = getattr(obj, "name", None) or getattr(obj, "title", None)
#     #     # context["profile_items"] = profile_items
#     #
#     #     return context/


# class ProfileEditView(DetailView):
#     model = Profile
#     template_name = "users/profile_edit.html"
#
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         u = self.object.user
#
#         user_form = UserUpdateForm(request.POST, instance=u)
#         profile_form = ProfileUpdateForm(
#             request.POST, request.FILES, instance=self.object
#         )
#
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             return redirect(self.object.get_absolute_url())
#
#         context = self.get_context_data(
#             user_form=user_form,
#             profile_form=profile_form
#         )
#         return self.render_to_response(context)
