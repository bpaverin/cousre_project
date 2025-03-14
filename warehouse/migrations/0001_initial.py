# Generated by Django 5.1.4 on 2024-12-27 12:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название/ФИО')),
                ('contact_person', models.CharField(blank=True, max_length=100, verbose_name='Контактное лицо')),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('address', models.TextField(verbose_name='Адрес')),
            ],
            options={
                'verbose_name': 'Клиент',
                'verbose_name_plural': 'Клиенты',
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Наименование')),
                ('description', models.TextField(verbose_name='Описание')),
                ('unit', models.CharField(max_length=20, verbose_name='Единица измерения')),
                ('current_quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Текущее количество')),
                ('min_quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Минимальный запас')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена за единицу')),
            ],
            options={
                'verbose_name': 'Стройматериал',
                'verbose_name_plural': 'Стройматериалы',
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название компании')),
                ('contact_person', models.CharField(max_length=100, verbose_name='Контактное лицо')),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('address', models.TextField(verbose_name='Адрес')),
            ],
            options={
                'verbose_name': 'Поставщик',
                'verbose_name_plural': 'Поставщики',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Количество')),
                ('order_date', models.DateField(auto_now_add=True, verbose_name='Дата заказа')),
                ('status', models.CharField(choices=[('new', 'Новый'), ('processing', 'В обработке'), ('completed', 'Выполнен'), ('cancelled', 'Отменён')], default='new', max_length=20, verbose_name='Статус')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.customer', verbose_name='Клиент')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.material', verbose_name='Материал')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='Supply',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Количество')),
                ('price_per_unit', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена за единицу')),
                ('delivery_date', models.DateField(verbose_name='Дата поставки')),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.material', verbose_name='Материал')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='warehouse.supplier', verbose_name='Поставщик')),
            ],
            options={
                'verbose_name': 'Поставка',
                'verbose_name_plural': 'Поставки',
            },
        ),
    ]
