from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

User = get_user_model()


# Actions to perform after a User model is saved
@receiver(post_save, sender=User)
def user_saved(sender, instance, created, **kwargs):
    # Actions for newly created User
    if created:
        # Create Profile
        profile = Profile(user=instance,)
        profile.save()

        print(f"Profile for {instance} Created!")

    # Actions for User updates
    elif not created:
        print("User Updated")
