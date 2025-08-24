from django.urls import path
from . import views

app_name = "market"
urlpatterns = [
    path("product/create/", views.ProductCreateView.as_view(), name="create-product"),
    path("products/", views.ProductListView.as_view(), name="home"),
    path("product/<int:pk>/", views.ProductDetailView.as_view(), name="product-detail"),
    path('favorites/toggle/<int:pk>/', views.toggle_favorite, name='toggle_favorite'),
    path("product/<int:product_id>/edit-images/", views.ProductImageEditView.as_view(), name="product-image-edit"),
    path("product/<int:product_id>/edit-details/", views.ProductDetailsUpdateView.as_view(), name="product-details-edit")
]