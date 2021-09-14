from django.contrib import admin
from .models import Recipe, Rating, Category

admin.site.register(Recipe)
admin.site.register(Rating)
admin.site.register(Category)
