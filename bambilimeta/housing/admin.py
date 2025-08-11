from django.contrib import admin
from .models import House, HouseImage, HouseReview


class HouseImageInline(admin.TabularInline):
    model = HouseImage
    extra = 1
    fields = ["image"]


class HouseAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ("title", "owner", "location", "created_at")

    def save_model(self, request, obj, form, change):
        """
        Set the owner to current user.
        Automatically sets the owner to the current user.
        This is a convenience feature to avoid having to manually set the owner.
        :param request: The HTTP request object.
        :param obj: The object being saved.
        :param form: The form data.
        :param change: Whether this is an update or create operation.
        :return: The saved object.


        """
        if not obj.pk:
            # If the object is being created, set the owner to the current user
            # This ensures that the owner is set only when creating a new house
            # and not when updating an existing one.
            # This is useful for ensuring that the owner is always set to the current user.
            # If the object already exists, we do not change the owner.
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        """
        Returns a list of read-only fields.

        This method is overridden to make the owner field read-only.
        This is useful for ensuring that the owner is always set to the current user and
        cannot be changed by the user.
        """
        if obj:  # Editing and existing house
            return self.readonly_fields + ("owner",)
        return self.readonly_fields

    inlines = [HouseImageInline]


admin.site.register(House, HouseAdmin)
admin.site.register(HouseImage)

admin.site.register(HouseReview)