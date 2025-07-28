from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from .models import House

#
# def house_list(request):
#     houses = House.objects.all()
#     return render(request, "housing/house_list.html", {"houses": houses})


class HouseListView(ListView):
    model = House
    paginate_by = 6


class HouseCreateView(CreateView):
    model = House
    fields = ["title", "location", "price", "description", "image", "video"]
    success_url = reverse_lazy("house_list")


class HouseDetailView(DetailView):
    model = House