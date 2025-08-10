# profiles/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, raw=False, using=None, update_fields=None, **kwargs):
    """
    Ensure every User has a Profile and keep it saved in sync.

    - On creation: create a related Profile.
    - On update: guarantee the Profile exists, then save it.

    Parameters:
    - sender: The model class sending the signal (User).
    - instance: The User instance just saved.
    - created (bool): True if this was a new User, else False.
    - raw (bool): True when loading raw data (fixtures). Skip side effects then.
    - using (str): Database alias used for the operation.
    - update_fields (set|None): Fields explicitly updated, if any.
    - **kwargs: For forward compatibility with extra signal args.
    """
    if raw:
        return  # Don’t create side effects during loaddata

    # Ensure a Profile exists (covers both freshly created and existing users)
    profile, _ = Profile.objects.get_or_create(user=instance)

    # If you need to react differently on creation, you still can:
    if created:
        profile.role = 'regular'
        ...

    # Save the profile to trigger any processing (e.g., image resize)
    profile.save(using=using)
