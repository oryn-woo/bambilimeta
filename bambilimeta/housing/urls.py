from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = "housing"
urlpatterns = [
    path("", views.HouseListView.as_view(), name="house_list"),
    path("upload/", views.HouseCreateView.as_view(), name="house_upload"),
    path("<int:pk>/", views.HouseDetailView.as_view(), name="house_detail"),
]


if settings.DEBUG:    # We do this only on debug mode.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
