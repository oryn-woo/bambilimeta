from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "auth"
urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("register/", views.Register.as_view(), name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="users/login.html"), name="login"),


]