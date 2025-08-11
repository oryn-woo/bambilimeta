from django.forms import BaseModelForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, View
from django.urls import reverse_lazy
from .models import House, HouseImage, HouseReview, Favorite
from .forms import CreateHouseForm, HouseImageFormSet, HouseReviewForm
from django.contrib.auth.decorators import login_required
# :TODO read
from django.contrib import messages
from django.db import transaction
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Exists, OuterRef, Value, BooleanField
from django.core.cache  import cache
from django.views.decorators.http import require_POST
from django.db.models import F
from .mixins import WelcomeMessageMixins
from .mixins import RoleAwareMessageMixin


class LandlordRequiredMixin(UserPassesTestMixin):
    """
    Test function for LandlordRequiredMixin.

    Ensures that the user requesting the resource has a profile with role == 'landlord'.
    If the user is unauthenticated, LoginRequiredMixin should redirect to login.
    If the user is authenticated but lacks a profile or has the wrong role,
    a message will be added to the request and the user will be redirected.
    """
    def test_func(self):
        """
        Test function for LandlordRequiredMixin.

        :return: True if the user has a profile with role == 'landlord', else False.
        """
        # safely get user object from request. If request has no user attribute, it returns None

        user = getattr(self.request, "user", None)

        # Ensure profile exists and role equals LandLord

        return bool(
            user and getattr(
                getattr(user, "profile", None),  # Tries getting the profile attribute from the user, if it deos not exist it returns None
                "role", None) == "landlord"  # Tries to get role attribute from the profile's it just got, else None
        )  # Final comparison compares the retrieve role if it's a land-lord and the boolean enforces Falsity, or Truth.

    def handle_no_permission(self):
        # if user is anonymous let parent handle (LoginRequiredMixin should handle it if included)
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()

        # Authenticated but not a landlord -> redirect with message
        messages.error(self.request, "You must be a lanlord to access this page")
        return redirect("housing:house-list")



class ViewCountMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        model = obj.__class__
        model.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
        return obj


from django.db.models import F
from django.utils.timezone import now

# class ViewCountMixin:
#     def get_object(self, queryset=None):
#         obj = super().get_object(queryset)
#         model = obj.__class__
#         model.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
#
#         # Optional: Log view
#         if self.request.user.is_authenticated:
#             model.viewlog_set.create(user=self.request.user, timestamp=now())
#         else:
#             ip = self.request.META.get("REMOTE_ADDR")
#             model.viewlog_set.create(ip_address=ip, timestamp=now())
#
#         return obj

# from django.db.models import F
# from functools import wraps
#
# def increment_view_count(model):
#     def decorator(view_func):
#         @wraps(view_func)
#         def _wrapped_view(request, *args, **kwargs):
#             pk = kwargs.get("pk")
#             if pk:
#                 model.objects.filter(pk=pk).update(view_count=F("view_count") + 1)
#             return view_func(request, *args, **kwargs)
#         return _wrapped_view
#     return decorator

# need a related ViewLog model with a ForeignKey to House, plus fields for user, ip_address, and timestamp.


class ReviewCreateReview(LoginRequiredMixin, CreateView):
    model = HouseReview
    form_class = HouseReviewForm
    template_name = "housing/review_form.html"

    def form_valid(self, form):
        """ Attach a house and author before saving so users dont have to pick at the interface."""
        house = get_object_or_404(House, pk=self.kwargs["pk"])
        form.instance.house = house
        form.instance.author = self.request.user
        messages.success(self.request, "Your review has been submitted successfully!")
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy("housing:house_detail", kwargs={"pk": self.kwargs["pk"]})


class HouseListView(WelcomeMessageMixins, ListView):
    model = House
    paginate_by = 6
    template_name = "housing/house_list.html"
    context_object_name = "houses"  # The variable name used in the template to loop through houses
    welcome_message = "Welcome to Bambili Rentals"
    def get_queryset(self):
        qs = House.objects.all()
        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=self.request.user,
                        house=OuterRef("pk")
                    )
                )
            )
        else:
            qs = qs.annotate(
                is_favorited=Value(
                    False, output_field=BooleanField()  # Ensures django does not guess field type
                )
            )
        return qs
    
    # def get(self, request, *args, **kwargs):
    #     """
    #     Handle GET requests and display a welcome message.
    #
    #     :param request: The HTTP request object.
    #     :param args: Additional positional arguments.
    #     :param kwargs: Additional keyword arguments.
    #     :return: The HTTP response from the parent class's GET method.
    #     """
    #     # Display an informational message to the user
    #     messages.info(request, "Welcome to bambili rentals!")
    #
    #     # Call the parent class's GET method to handle the request
    #     return super().get(request, *args, **kwargs)

    # def dispatch(self, request, *args, **kwargs):
    #     """ Handle the request and display a welcome message. And is more cleaner than using get method."""
    #     messages.info(request, "Welcom to bambili rentals!")
    #     # Call the parent class's dispatch method to handle the request
    #     return super().dispatch(request, *args, **kwargs)



    def get_context_data(self, *, object_list=None, **kwargs):
        """
        Add extra data to the template context for the house list view.

        :param object_list: The list of objects in the view (in this case, House objects).
        :param kwargs: Additional keyword arguments.
        :return: The updated context dictionary.
        """
        context = super().get_context_data(**kwargs)  # The original data

        # Add a list of 3 featured houses to the context.
        # These are used on the house list page.

        # Fetch cache hero homes.
        popular_houses = cache.get("popular_houses")
        if not popular_houses:
            popular_houses = list(House.objects.order_by("-view_count")[:2])
            cache.set("popular_houses", popular_houses, 900)  # Cache for 24 hours
        context["popular_houses"] = popular_houses
        hero_homes = cache.get("hero_home_list")
        if not hero_homes:
            hero_homes = list(House.objects.all()[:3])

            # Caching time
            cache.set("hero_home_list", hero_homes, 900)  # Cache for 24 hours
        context["hero_homes"] = hero_homes

        # If the user has navigated to the house list page from the home page, set
        # a flag in the context so that the template can show the hero section welcoming
        # them to the house list page.
        context = super().get_context_data(**kwargs) # The origianl data
        context["hero_homes"] = House.objects.all()[:3]  # Additional data
        from_home = self.request.GET.get("focus") == "yes"
        context["focused"] = from_home

        return context


class HouseCreateView(LoginRequiredMixin, View):
    """
    A raw view is used to handle HTTP request.
    This class is designed to identify and map methods to their
     corresponding HTTP request types.
    Each method requires the args and kwargs to capture parameters form the url, e.g., ID.
    - Creating the house object
    - Create multiple image objects linked to it.
    Mixin oder matters, LoginRequiredMixin comes before UserPassTestMixin so unauthenticated users are redirect to login instead of 403
    Defence-in-depth: the mixin checks hasattr(user, 'profile') (in case signals didn't run yet).
    Saving: transaction.atomic() ensures house + images save together.

    """
    login_url = reverse_lazy("auth:login")
    redirect_field_name = "next"
    def get(self, request, *args, **kwargs):
        """
        A get request renders the form.
        :param request: Request object
        :return: Template and context.
        """
        print("get method triggered")
        house_form = CreateHouseForm()  # Standard house form
        formset = HouseImageFormSet(
            queryset=HouseImage.objects.none()  # Prevent existing image from showing up
        )
        return render(request, "housing/house_form.html",
                      {
                          "form": house_form,
                          "formset": formset
                      })

    def post(self, request, *args, **kwargs):
        """
        Handles form submission.
        :param request: The HTTP request object, which contains all details about incoming request.
         (form data, headers, method type)
        :return: Template and context.
        """
        print("Post method triggered")
        house_form = CreateHouseForm(request.POST)
        formset = HouseImageFormSet(
            request.POST,
            request.FILES,
            queryset=HouseImage.objects.none()
        )  # Collect form data

        if house_form.is_valid() and formset.is_valid():

            try:
                with transaction.atomic():
                    # save house
                    house = house_form.save(commit=False)
                    # Attach owner/land-lord (make sure House model has an 'owner' or land-lord
                    house.owner = request.user
                    house.save()
                    # save formset images
                    for img in formset.cleaned_data:
                        # formset.cleaned data contains dict for each form or and empty dict
                        if not img:
                            continue
                        image = img.get("image")
                        caption = img.get("caption") or ""
                        if image:
                            HouseImage.objects.create(house=house, image=image)
                messages.success(request, "House Created successful")
                return redirect("housing:house_detail")
            except Exception as exc:
                # log exception
                messages.error(request, f"The was a problem saving house {exc}")
        else:
            messages.error(request, "please correct errors below")

        return render(request, "housing/house_form.html", {
            "form": house_form,
            "formset": formset
        })


class HouseDetailView(DetailView, ViewCountMixin):
    model = House
    template_name = "housing/house_detail.html"
    context_object_name = "house_detail"

    # def get_object(self, queryset=None):
    #     """
    #     In Django’s class-based views (like DetailView), get_object() is responsible for retrieving the object that the view will display.
    #      obj = super().get_object(queryset)
    #
    #     :param queryset:
    #     :return:
    #     """
    #     obj = super().get_object(queryset)  # This line calls the parent method to fetch the object—say, a House with pk=5
    #     House.objects.filter(pk=obj.pk).update(view_count=F("view_count") + 1)
    #     update() performs direct SQL database UPDATE without going through model.save()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        house = self.get_object()
        context["reviews"] = house.reviews.all().order_by('-reviewed_on')
        context["review_form"] = HouseReviewForm()
        return context


@login_required
def add_favorite(request, house_id):
    """
    Add a house to the user's favorites.

    :param request: HTTP request
    :param house_id: ID of the house to add to favorites
    :return: JSON response with a success message
    """
    # Get the house object
    house = get_object_or_404(House, id=house_id)

    # Create or get the favorite object
    Favorite.objects.get_or_create(user=request.user, house=house)

    # Return a JSON response
    return JsonResponse({"message": "House added to favorites."}, status=200)


@login_required
def remove_favorite(request, house_id):
    """
    Remove a house from the user's favorites

    :param request: HTTP request
    :param house_id: ID of the house to remove from favorites
    :return: JSON response with a success message
    """
    # Get the house object
    house = get_object_or_404(House, id=house_id)

    # Delete the favorite object
    Favorite.objects.filter(user=request.user, house=house).delete()

    # Return a JSON response with a success message
    return JsonResponse({"message": "House removed from favorites."}, status=200)


@login_required
def favorite_list(request):
    """
    View to list the user's favorites.

    :param request: The HTTP request object.
    :return: The rendered template.
    """
    # select_related is used to avoid a database query for each favorite to get the house
    favorites = Favorite.objects.filter(user=request.user).select_related('house')

    # Render the template with the favorites
    return render(request, "housing/house_list.html", {"favorites": favorites})


class FavouriteListView(LoginRequiredMixin, ListView):
    """
    A view to list the user's favorite houses.
    """
    model = House
    template_name = "housing/favorite_list.html"
    context_object_name = "favorites"

    def get_queryset(self):
        """
        Get the list of houses that are favorited by the user.

        :return: A QuerySet of House objects that are favorited by the user.
        """
        # Get only houses favorited by user
        qs = House.objects.filter(
            favorites__user=self.request.user
        ).distinct()

        # Annotate is_favorited for template logic (always true)
        qs = House.objects.filter(favorites__user=self.request.user).distinct()  # distinct avoid duplicates.

        # Annotate is_favorited for template logic (always true)
        qs = qs.annotate(
            is_favorited=Value(True, output_field=BooleanField())
        ).prefetch_related("favorites")  # prefetch_related is used to avoid a database query for each favorite to get the house

        # Return the QuerySet
        return qs


@require_POST
@login_required
def toggle_favorite(request):
    house_id = request.POST.get("house_id")
    house = get_object_or_404(House, pk=house_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user, house=house
    )
    if not created:
        favorite.delete()
    return JsonResponse({"is_favorited": created})