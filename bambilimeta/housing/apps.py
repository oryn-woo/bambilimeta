from django.apps import AppConfig


class HousingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'housing'

    def ready(self):
        import housing.signals # This ensures the signal is registered and loaded early.

