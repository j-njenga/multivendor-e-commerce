# Generated by Django 4.2.7 on 2023-11-17 07:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_order_alter_product_image_alter_product_thumbnail_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='merchant_id',
            new_name='payment_intent',
        ),
    ]
