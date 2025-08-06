from django.urls import path

from . import views

app_name = "housing"
urlpatterns = [
    path("", views.HouseListView.as_view(), name="house-list"),
    path("upload/", views.HouseCreateView.as_view(), name="house_upload"),
    path("house/<int:pk>/", views.HouseDetailView.as_view(), name="house_detail"),
    path("house/<int:pk>/review/", views.ReviewCreateReview.as_view(), name="house_review")
]
