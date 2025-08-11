from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import House

@receiver([post_save, post_delete], sender=House)
def refresh_hero_home_cache(sender, **kwargs):
    """
    This ensures cache is always fresh when data changes
    Well the post_save and post_delete signals are fired when a model is saved, updated or deleted, and
     a call is made to the receiver function. The receiver function refreshes the cache by
     retrieving a list of the first three houses and storing it in the cache.
    :param sender:
    :param kwargs:
    :return:
    """
    hero_homes = list(House.objects.all()[:2])
    cache.set("hero_home_list", hero_homes, 900)