from django.contrib import messages


class WelcomeMessageMixins:
    """
    The welcome_message is the default message that will be displayed to the user
    if the view explicitly does provide a message, it takes precedence
    """
    welcome_message = None
    def get_welcome_message(self):
        return self.welcome_message 

    def dispatch(self, request, *args, **kwargs):
        message = self.get_welcome_message()
        if message:
            messages.info(request, message)
        return super().dispatch(request, *args, **kwargs)


class RoleAwareMessageMixin:
    welcome_message = None

    def get_welcome_message(self):
        return self.welcome_message or "Welcome to Bambili Rentals"

    def dispatch(self, request, *args, **kwargs):
        message = self.get_welcome_message()
        if message:
            if request.user.is_authenticated:
                role = getattr(request.user.profile, "role", None)
                if role == "landlord":
                    messages.info(request, message)
                elif role == "entrepreneur":
                    messages.info(request, message)
                elif request.user.is_superuser:
                    messages.info(request, message)
            else:
                messages.info(request, message)
        return super().dispatch(request, *args, **kwargs)