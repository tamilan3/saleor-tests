# Generated by Django 4.2.16 on 2024-09-14 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0197_tag_product_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='products', to='product.tag'),
        ),
    ]
