import decimal
import environ

from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from users.models import Profile

env = environ.Env()
environ.Env.read_env()


class ImageAlbum(models.Model):
    """
    Image Album model for relating many images to a recipe
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    def default(self):
        return self.images.filter(default=True).first()

    def thumbnails(self):
        return self.images.filter(width__lt=100, length_lt=100)


class Image(models.Model):
    """
    Image model
    """
    name = models.CharField(max_length=255)
    # image = models.ImageField(upload_to='recipes/', blank=True, null=True, default=None)
    image = CloudinaryField('image',
                            overwrite=True,
                            folder=env('CLOUD_DIR'),
                            resource_type="image",
                            use_filename=True,
                            unique_filename=False,
                            format="jpg",
                            default=None)
    submitted_by = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True)
    default = models.BooleanField(default=False)
    album = models.ForeignKey(ImageAlbum, related_name='images', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, unique=True)
    submitted_by = models.ForeignKey(Profile, on_delete=models.CASCADE, default=None, null=True)
    average_rating = models.DecimalField(max_digits=2, decimal_places=1, blank=True, default=0.0)
    category = models.ManyToManyField(Category, blank=True, default=None)
    description = models.TextField(blank=True, null=True, default=None)
    prep_time = models.IntegerField(blank=True, null=True, default=None)
    cook_time = models.IntegerField(blank=True, null=True, default=None)
    total_time = models.IntegerField(blank=True, null=True, default=None)
    servings = models.IntegerField(blank=True, null=True, default=None)
    likes = models.ManyToManyField(Profile, blank=True, related_name="likes")
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now_add=True, blank=True)
    ingredients = models.TextField(blank=True, default=None)
    steps = models.TextField(blank=True, default=None)
    nutrition = models.TextField(blank=True, null=True, default=None)
    album = models.OneToOneField(ImageAlbum, related_name='recipe', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_avg_rating(self):
        ratings = Rating.objects.filter(recipe=self)
        count = len(ratings)
        total = 0
        for rating in ratings:
            total += rating.rating
        return decimal.Decimal(total / count)


class Rating(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f"{self.profile} rates {self.recipe} a {self.rating}/5"
