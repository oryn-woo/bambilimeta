from django.forms import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, View
from django.urls import reverse_lazy
from .models import House, HouseImage, HouseReview
from .forms import CreateHouseForm, HouseImageFormSet, HouseReviewForm


class ReviewCreateReview(CreateView):
    model = HouseReview
    form_class = HouseReviewForm
    template_name = "housing/review_form.html"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        """ Attach a house before saving so users dont have to pick at the interface."""
        house = get_object_or_404(House, pk=self.kwargs["pk"])
        form.instance.house = house
        return super().form_valid(form)





class HouseListView(ListView):
    model = House
    paginate_by = 6


class HouseCreateView(View):
    """
    A raw view is used to handle HTTP request.
    This class is designed to identify and map methods to their
     corresponding HTTP request types.
    Each method requires the args and kwargs to capture parameters form the url, e.g., ID.
    - Creating the house object
    - Create multiple image objects linked to it.
    """
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
            house = house_form.save()
            for form in formset:
                if form.cleaned_data.get("image"):
                    image = form.save(commit=False)
                    image.house = house
                    image.save()
            return redirect(house.get_absolute_url())
        return render(request, "housing/house_form.html", {
            "form": house_form,
            "formset": formset
        })


class HouseDetailView(DetailView):
    model = House
    template_name = "housing/house_detail_2.html"
    context_object_name = "house_detail"
    def get_context_data(self, **kwargs:reverse_lazy) :
        context = super().get_context_data(**kwargs)
        context["reviews"] = HouseReview.objects.all()
        return context
     