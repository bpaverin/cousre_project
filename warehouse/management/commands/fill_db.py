from django.core.management.base import BaseCommand
from warehouse.models import Supplier, Material, Supply, Customer, Order, Category
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta


class Command(BaseCommand):
    help = 'Fills database with sample data'

    def handle(self, *args, **options):
        # Очищаем БД
        Supplier.objects.all().delete()
        Material.objects.all().delete()
        Customer.objects.all().delete()
        Category.objects.all().delete()

        # Создаем категории
        categories = [
            Category.objects.create(name='Сыпучие материалы'),
            Category.objects.create(name='Пиломатериалы'),
            Category.objects.create(name='Кирпич и блоки'),
            Category.objects.create(name='Металлопрокат'),
            Category.objects.create(name='Отделочные материалы'),
        ]

        # Создаем поставщиков
        suppliers = [
            Supplier.objects.create(
                name='ООО "СтройМастер"',
                contact_person='Иванов Иван',
                phone='+7 (999) 123-45-67',
                address='г. Москва, ул. Строительная, 1',
                email='stroymaster@example.com'
            ),
            Supplier.objects.create(
                name='ИП Петров С.М.',
                contact_person='Петров Сергей',
                phone='+7 (999) 765-43-21',
                address='г. Санкт-Петербург, пр. Металлистов, 10',
                email='petrov@example.com'
            ),
            Supplier.objects.create(
                name='ЗАО "ЦементГрупп"',
                contact_person='Сидорова Анна',
                phone='+7 (999) 555-55-55',
                address='г. Новосибирск, ул. Промышленная, 5',
                email='cement@example.com'
            ),
        ]

        # Создаем материалы
        materials = [
            Material.objects.create(
                name='Цемент М500',
                description='Портландцемент высшего качества',
                unit='кг',
                category=categories[0],
                quantity=Decimal('0.00')
            ),
            Material.objects.create(
                name='Брус 150x150',
                description='Строганный брус из сосны',
                unit='м³',
                category=categories[1],
                quantity=Decimal('0.00')
            ),
            Material.objects.create(
                name='Кирпич красный',
                description='Облицовочный кирпич',
                unit='шт',
                category=categories[2],
                quantity=Decimal('0.00')
            ),
            Material.objects.create(
                name='Песок строительный',
                description='Мытый речной песок',
                unit='м³',
                category=categories[0],
                quantity=Decimal('0.00')
            ),
            Material.objects.create(
                name='Арматура 12мм',
                description='Стальная арматура А400',
                unit='м',
                category=categories[3],
                quantity=Decimal('0.00')
            ),
            Material.objects.create(
                name='Гипсокартон',
                description='Листы ГКЛ 2500х1200х12.5',
                unit='шт',
                category=categories[4],
                quantity=Decimal('0.00')
            ),
        ]

        # Создаем клиентов
        customers = [
            Customer.objects.create(
                name='ООО "Застройщик"',
                contact_person='Николаев Павел',
                phone='+7 (999) 111-22-33',
                address='г. Москва, ул. Девелоперская, 15',
                email='zastroy@example.com'
            ),
            Customer.objects.create(
                name='Михайлов Андрей Петрович',
                contact_person='Михайлов Андрей',
                phone='+7 (999) 444-55-66',
                address='г. Химки, ул. Дачная, 7',
                email='mikhailov@example.com'
            ),
            Customer.objects.create(
                name='ИП Васильева Т.Н.',
                contact_person='Васильева Татьяна',
                phone='+7 (999) 777-88-99',
                address='г. Подольск, ул. Строителей, 3',
                email='vasileva@example.com'
            ),
        ]

        # Создаем поставки
        for _ in range(20):
            material = random.choice(materials)
            quantity = Decimal(random.randint(10, 1000))
            price_per_unit = Decimal(random.randint(100, 1000))

            Supply.objects.create(
                supplier=random.choice(suppliers),
                material=material,
                quantity=quantity,
                price_per_unit=price_per_unit,
                total_cost=quantity * price_per_unit,
                arrival_time=timezone.now() - timedelta(days=random.randint(1, 30))
            )

        # Создаем заказы
        for _ in range(15):
            material = random.choice(materials)
            quantity = Decimal(random.randint(1, 100))
            price_per_unit = Decimal(random.randint(100, 1000))

            Order.objects.create(
                customer=random.choice(customers),
                material=material,
                quantity=quantity,
                total_sum=quantity * price_per_unit,
                order_datetime=timezone.now() - timedelta(days=random.randint(1, 30))
            )

        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена тестовыми данными'))
