from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from decimal import Decimal


class Supplier(models.Model):
    name = models.CharField('Название компании', max_length=100)
    contact_person = models.CharField('Контактное лицо', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    address = models.TextField('Адрес')
    email = models.EmailField('Email', max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


class Customer(models.Model):
    name = models.CharField('Название/ФИО', max_length=100)
    contact_person = models.CharField('Контактное лицо', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    address = models.TextField('Адрес')
    email = models.EmailField('Email', max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'


class Category(models.Model):
    name = models.CharField('Название категории', max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Material(models.Model):
    name = models.CharField('Наименование', max_length=100)
    description = models.TextField('Описание')
    unit = models.CharField('Единица измерения', max_length=20)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name='Категория', null=True)
    quantity = models.DecimalField('Количество', max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    class Meta:
        verbose_name = 'Материал'
        verbose_name_plural = 'Материалы'


class Supply(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='Материал')
    quantity = models.DecimalField('Количество', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    arrival_time = models.DateTimeField('Время прибытия', default=timezone.now)
    price_per_unit = models.DecimalField('Цена за единицу', max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_cost = models.DecimalField('Полная стоимость', max_digits=12, decimal_places=2, default=Decimal('0.00'))
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name='Поставщик')

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * self.price_per_unit
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Поставка {self.material} от {self.supplier}"

    class Meta:
        verbose_name = 'Поставка'
        verbose_name_plural = 'Поставки'


class Order(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    material = models.ForeignKey('Material', on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    total_sum = models.DecimalField(max_digits=10, decimal_places=2)
    order_datetime = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ {self.id} от {self.customer.name}'


# Сигналы для автоматического обновления количества материалов
@receiver(post_save, sender=Supply)
def update_material_quantity_on_supply(sender, instance, created, **kwargs):
    if created:  # Только для новых поставок
        material = instance.material
        material.quantity += instance.quantity
        material.save()


@receiver(post_save, sender=Order)
def update_material_quantity_on_order(sender, instance, created, **kwargs):
    if created:  # Только для новых заказов
        material = instance.material
        material.quantity -= instance.quantity
        material.save()
