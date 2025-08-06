from django.contrib import admin
from .models import House, HouseImage, HouseReview


class HouseImageInline(admin.TabularInline):
    model = HouseImage
    extra = 1
    fields = ["image"]


class HouseAdmin(admin.ModelAdmin):
    inlines = [HouseImageInline]


admin.site.register(House, HouseAdmin)
admin.site.register(HouseImage)

admin.site.register(HouseReview)