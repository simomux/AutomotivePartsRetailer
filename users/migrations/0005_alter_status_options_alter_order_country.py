# Generated by Django 5.0.6 on 2024-07-02 16:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_product_amount_bought_product_discount_price_and_more'),
        ('users', '0004_payment_status_order_cartitem_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='status',
            options={'verbose_name_plural': 'Statuses'},
        ),
        migrations.AlterField(
            model_name='order',
            name='country',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.country'),
        ),
    ]
