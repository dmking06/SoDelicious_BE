from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Recipe, ImageAlbum


# Actions to perform after a Recipe is saved
@receiver(post_save, sender=Recipe)
def user_saved(sender, instance, created, **kwargs):
    # Actions for newly created Recipe
    if created:
        # Create ImageAlbum and save to Recipe
        album = ImageAlbum(name=f"{instance.name} album")
        album.save()

        instance.album = album
        instance.save()

        print(f"Album for {instance} recipe created and attached!")

    # Actions for User updates
    elif not created:
        print("Recipe Updated")
