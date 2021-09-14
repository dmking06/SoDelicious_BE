from cloudinary.models import CloudinaryField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import Profile


def get_upload_path(instance, filename):
    """
    Returns the upload path for a given image
    :param instance: Image instance
    :param filename: name of image file
    :return: path to image file
    """
    model = instance.album.model.__class__._meta
    name = model.verbose_name_plural.replace(' ', '_')
    pk = model.pk
    return f'recipes/{name}_{pk}/{filename}'


class ImageAlbum(models.Model):
    """
    Image Album model for relating many images to a recipe
    """
    def default(self):
        return self.images.filter(default=True).first()

    def thumbnails(self):
        return self.images.filter(width__lt=100, length_lt=100)


class Image(models.Model):
    """
    Image model
    """
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to=get_upload_path)
    default = models.BooleanField(default=False)
    album = models.ForeignKey(ImageAlbum, related_name='images', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    submitted_by = models.ForeignKey(Profile, on_delete=models.CASCADE, default=None)
    category = models.ManyToManyField(Category, blank=True, default=None)
    description = models.TextField(blank=True, null=True, default=None)
    prep_time = models.IntegerField(blank=True, null=True, default=None)
    cook_time = models.IntegerField(blank=True, null=True, default=None)
    total_time = models.IntegerField(blank=True, null=True, default=None)
    servings = models.IntegerField(blank=True, null=True, default=None)
    likes = models.ManyToManyField(Profile, blank=True, related_name="likes")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True, blank=True)
    ingredients = models.TextField(blank=True, null=True, default=None)
    steps = models.TextField(blank=True, null=True, default=None)
    nutrition = models.TextField(blank=True, null=True, default=None)
    album = models.OneToOneField(ImageAlbum, related_name='model', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Rating(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True,
                                 default=0, validators=[MinValueValidator(0), MaxValueValidator(5)])
