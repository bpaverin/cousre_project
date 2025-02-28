# Generated by Django 5.1.6 on 2025-02-28 10:58

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse', '0002_category_alter_material_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.customer'),
        ),
        migrations.AlterField(
            model_name='order',
            name='material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.material'),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_datetime',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='order',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_sum',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
