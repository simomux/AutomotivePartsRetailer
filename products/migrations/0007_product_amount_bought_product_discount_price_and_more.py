# Generated by Django 5.0.6 on 2024-06-27 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_product_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='amount_bought',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='product',
            name='discount_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='is_discount',
            field=models.BooleanField(default=False),
        ),
    ]
