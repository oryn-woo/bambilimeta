from django.urls import path

from . import views

app_name = "housing"
urlpatterns = [
    path("", views.HouseListView.as_view(), name="house-list"),
    path("upload/", views.HouseCreateView.as_view(), name="house_upload"),
    path("house/<int:pk>/", views.HouseDetailView.as_view(), name="house_detail"),
    path("house/<int:pk>/review/", views.ReviewCreateReview.as_view(), name="house_review"),
    # path("favorites/add/<int:house_id>/", views.add_favorite, name="add_favorite"),
    # path("favorites/remove/<int:house_id>/", views.remove_favorite, name="remove_favorite"),
    path("favorites/", views.FavouriteListView.as_view(), name="favorite_list"),
    path("favorite-toggle/", views.toggle_favorite, name="favorite_toggle"),
]
