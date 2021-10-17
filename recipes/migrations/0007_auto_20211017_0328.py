# Generated by Django 3.2.7 on 2021-10-17 07:28

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_alter_image_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='cloud_image',
            field=cloudinary.models.CloudinaryField(default=None, max_length=255, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='image',
            name='image',
            field=models.ImageField(blank=True, default=None, null=True, upload_to='recipes/'),
        ),
    ]
