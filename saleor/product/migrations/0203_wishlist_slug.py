# Generated by Django 4.2.16 on 2024-09-22 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0202_wishlist_metadata_wishlist_private_metadata_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='wishlist',
            name='slug',
            field=models.SlugField(allow_unicode=True, default=1, max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
