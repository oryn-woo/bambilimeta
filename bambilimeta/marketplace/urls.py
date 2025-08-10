from django.urls import path
from . import views

app_name = "market"
urlpatterns = [
    path("products/create/", views.ProductCreateView.as_view(), name="product_create"),
    path("products/", views.ProductListView.as_view(), name="products"),
    path("products/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),

]