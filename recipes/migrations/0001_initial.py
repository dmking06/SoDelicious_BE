# Generated by Django 3.2.7 on 2021-09-24 18:09

import cloudinary.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('image', cloudinary.models.CloudinaryField(blank=True, default=None, max_length=255, null=True, verbose_name='image')),
                ('default', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ImageAlbum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.DecimalField(blank=True, decimal_places=1, default=0, max_digits=2, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)])),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, default=None)),
                ('prep_time', models.IntegerField(blank=True, default=None)),
                ('cook_time', models.IntegerField(blank=True, default=None)),
                ('total_time', models.IntegerField(blank=True, default=None)),
                ('servings', models.IntegerField(blank=True, default=None)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now_add=True)),
                ('ingredients', models.TextField(blank=True, default=None)),
                ('steps', models.TextField(blank=True, default=None)),
                ('nutrition', models.TextField(blank=True, default=None)),
                ('album', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipe', to='recipes.imagealbum')),
                ('category', models.ManyToManyField(blank=True, default=None, to='recipes.Category')),
            ],
        ),
    ]
