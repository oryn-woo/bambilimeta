from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

app_name = "auth"
urlpatterns = [
    # path("profile/", views.profile, name="profile"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
    path("logout/", auth_view.LogoutView.as_view(template_name="users/logout.html"), name="logout")


]