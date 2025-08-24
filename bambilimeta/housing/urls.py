from django.urls import path

from . import views

app_name = "housing"
urlpatterns = [
    path("", views.HouseListView.as_view(), name="home"),
    path("upload/", views.HouseCreateView.as_view(), name="upload-house"),

    path("house-edit/<int:pk>/edit-house-images/", views.HouseImageEdit.as_view(), name="edit-house-images"),
    path("house-edit/<int:pk>/edit-house-details/", views.HouseDetailEditView.as_view(), name="edit-house-details"),

    path("house/<int:pk>/", views.HouseDetailView.as_view(), name="house-detail"),
    path("house/<int:pk>/review/", views.ReviewCreateReview.as_view(), name="house-review"),
    # path("favorites/add/<int:house_id>/", views.add_favorite, name="add_favorite"),
    # path("favorites/remove/<int:house_id>/", views.remove_favorite, name="remove_favorite"),
    path("favorites/", views.FavouriteListView.as_view(), name="favorites"),
    path("favorite-toggle/", views.toggle_favorite, name="favorite_toggle"),
]
