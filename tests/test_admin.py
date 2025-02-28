import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from warehouse.models import Material, Supply, Order, Category, Customer, Supplier
from decimal import Decimal
from django.utils import timezone

@pytest.mark.django_db
class TestAdmin:
    @pytest.fixture
    def admin_user(self):
        return User.objects.create_superuser('admin', 'admin@test.com', 'password')

    @pytest.fixture
    def admin_client(self, admin_user):
        client = Client()
        client.login(username='admin', password='password')
        return client

    @pytest.fixture
    def category(self):
        return Category.objects.create(name='Test Category')

    @pytest.fixture
    def material(self, category):
        return Material.objects.create(
            name='Test Material',
            description='Test Description',
            unit='pcs',
            category=category,
            quantity=Decimal('10.00')
        )

    @pytest.fixture
    def supplier(self):
        return Supplier.objects.create(
            name='Test Supplier',
            contact_person='John Doe',
            phone='+1234567890',
            address='Test Address',
            email='supplier@test.com'
        )

    @pytest.fixture
    def customer(self):
        return Customer.objects.create(
            name='Test Customer',
            contact_person='Jane Doe',
            phone='+1234567890',
            address='Test Address',
            email='customer@test.com'
        )

    @pytest.fixture
    def supply(self, material, supplier):
        return Supply.objects.create(
            material=material,
            quantity=Decimal('10.00'),
            price_per_unit=Decimal('100.00'),
            supplier=supplier,
            arrival_time=timezone.now()
        )

    @pytest.fixture
    def order(self, material, customer):
        return Order.objects.create(
            material=material,
            customer=customer,
            quantity=Decimal('5.00'),
            total_sum=Decimal('500.00')
        )

    def test_material_admin_crud(self, admin_client, category):
        # Проверка создания материала через админку
        material_data = {
            'name': 'New Material',
            'description': 'New Description',
            'unit': 'kg',
            'category': category.id,
            'quantity': '20.00'
        }
        response = admin_client.post(
            reverse('admin:warehouse_material_add'),
            material_data
        )
        assert response.status_code == 302  # redirect after success
        assert Material.objects.filter(name='New Material').exists()

        # Проверка редактирования
        material = Material.objects.get(name='New Material')
        edit_data = material_data.copy()
        edit_data['name'] = 'Updated Material'
        response = admin_client.post(
            reverse('admin:warehouse_material_change', args=[material.id]),
            edit_data
        )
        assert response.status_code == 302
        assert Material.objects.filter(name='Updated Material').exists()

        # Проверка удаления
        response = admin_client.post(
            reverse('admin:warehouse_material_delete', args=[material.id]),
            {'post': 'yes'}
        )
        assert response.status_code == 302
        assert not Material.objects.filter(name='Updated Material').exists()

    def test_supply_admin_validation(self, admin_client, material, supplier):
        # Проверка создания поставки с отрицательным количеством
        supply_data = {
            'material': material.id,
            'supplier': supplier.id,
            'quantity': '-10.00',
            'price_per_unit': '100.00',
            'arrival_time': timezone.now()
        }
        response = admin_client.post(
            reverse('admin:warehouse_supply_add'),
            supply_data
        )
        assert response.status_code == 200  # форма не прошла валидацию
        assert 'error' in str(response.content)

    def test_order_admin_validation(self, admin_client, material, customer):
        # Сначала установим начальное количество материала
        material.quantity = Decimal('50.00')
        material.save()

        # Проверка создания заказа с количеством больше доступного
        order_data = {
            'material': material.id,
            'customer': customer.id,
            'quantity': '100.00',  # больше чем есть в наличии
            'total_sum': '10000.00',
            '_save': 'Сохранить'
        }
        response = admin_client.post(
            reverse('admin:warehouse_order_add'),
            order_data
        )
        
        # Проверяем, что форма вернулась с ошибкой
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert 'Недостаточное количество материала на складе' in content

        # Проверяем успешное создание заказа с допустимым количеством
        valid_order_data = {
            'material': material.id,
            'customer': customer.id,
            'quantity': '20.00',  # меньше чем есть в наличии
            'total_sum': '2000.00',
            '_save': 'Сохранить'
        }
        response = admin_client.post(
            reverse('admin:warehouse_order_add'),
            valid_order_data,
            follow=True
        )

        # Проверяем, что заказ был создан успешно
        assert response.status_code == 200
        assert Order.objects.filter(quantity=Decimal('20.00')).exists()

        # Проверяем, что количество материала уменьшилось
        material.refresh_from_db()
        assert material.quantity == Decimal('30.00')  # 50 - 20 = 30

    def test_supply_admin_date_hierarchy(self, admin_client, supply):
        url = reverse('admin:warehouse_supply_changelist')

        # Проверка иерархии по дате
        year = timezone.now().strftime('%Y')
        month = timezone.now().strftime('%m')

        response = admin_client.get(f"{url}?arrival_time__year={year}&arrival_time__month={month}")
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert supply.material.name in content

    def test_order_admin_list_display(self, admin_client, order):
        url = reverse('admin:warehouse_order_changelist')
        response = admin_client.get(url)

        # Проверка отображения полей
        assert response.status_code == 200
        content = response.content.decode('utf-8')

        # Проверяем наличие данных в таблице
        assert str(order.id) in content
        assert order.customer.name in content
        assert order.material.name in content

        # Проверяем, что числа отображаются в таблице (они могут быть отформатированы)
        quantity_str = str(int(order.quantity)) # проверяем только целую часть
        assert quantity_str in content

        total_sum_str = str(int(order.total_sum)) # проверяем только целую часть
        assert total_sum_str in content

    def test_admin_permissions(self, client, material):
        # Проверка доступа без авторизации
        url = reverse('admin:warehouse_material_changelist')
        response = client.get(url)
        assert response.status_code == 302  # редирект на страницу логина
        assert '/admin/login/' in response.url

    def test_material_admin_list_filters(self, admin_client, material):
        url = reverse('admin:warehouse_material_changelist')

        # Проверка фильтрации по категории
        response = admin_client.get(url, {'category__id__exact': material.category.id})
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert material.name in content

        # Проверка поиска
        response = admin_client.get(url, {'q': material.name})
        assert response.status_code == 200
        content = response.content.decode('utf-8')
        assert material.name in content
