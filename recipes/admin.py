from django.contrib import admin
from .models import Recipe, Rating, Category, Image, ImageAlbum

admin.site.register(Recipe)
admin.site.register(Rating)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(ImageAlbum)
