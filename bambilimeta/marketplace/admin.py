from django.contrib import admin
from .forms import ImageInlineFormset
admin.site.site_header = "Bambili Marketplace Admin"
admin.site.site_title = "Bambili Marketplace Admin Portal"
admin.site.index_title = "Welcome to the Bambili Marketplace Admin Portal"
from .models import Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    fields = ("image",)
    extra = 3


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "stock", "description", "created_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    inlines = [ProductImageInline]