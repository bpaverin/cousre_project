import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import LiveServerTestCase
from warehouse.models import Material, Category
from decimal import Decimal
import csv
import os

@pytest.fixture
def driver():
    # Инициализация драйвера Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Запуск в фоновом режиме
    # Настраиваем папку для загрузки файлов
    download_dir = os.path.join(os.getcwd(), 'test_downloads')
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    options.add_experimental_option('prefs', {
        'download.default_directory': download_dir,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    })
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)  # Добавляем неявное ожидание
    yield driver
    # Очищаем папку с загрузками после теста
    for file in os.listdir(download_dir):
        os.remove(os.path.join(download_dir, file))
    os.rmdir(download_dir)
    driver.quit()

@pytest.mark.django_db
class TestAdminPanel:
    def test_admin_login_and_navigation(self, driver, live_server):
        # Создаем суперпользователя
        User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )

        # Переходим на страницу входа в админку
        driver.get(f'{live_server.url}/admin/')

        # Проверяем, что мы на странице логина
        assert 'Войти' in driver.page_source

        # Вводим логин и пароль
        username_input = driver.find_element(By.NAME, 'username')
        username_input.send_keys('admin')
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys('admin123')
        password_input.submit()

        # Ждем загрузки главной страницы админки
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'dashboard'))
        )

        # Проверяем, что мы успешно вошли
        assert 'Система управления складом стройматериалов' in driver.page_source

        # Проверяем наличие основных разделов
        assert 'WAREHOUSE' in driver.page_source.upper()

        # Делаем скриншот для отладки
        driver.save_screenshot('admin_dashboard.png')

    def test_export_materials_to_csv(self, driver, live_server):
        # Создаем тестовые данные
        category = Category.objects.create(name='Test Category')
        Material.objects.create(
            name='Test Material 1',
            description='Description 1',
            unit='pcs',
            category=category,
            quantity=Decimal('10.00')
        )
        Material.objects.create(
            name='Test Material 2',
            description='Description 2',
            unit='kg',
            category=category,
            quantity=Decimal('20.00')
        )

        # Создаем и логиним админа
        User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        driver.get(f'{live_server.url}/admin/')
        driver.find_element(By.NAME, 'username').send_keys('admin')
        driver.find_element(By.NAME, 'password').send_keys('admin123')
        driver.find_element(By.NAME, 'password').submit()

        # Переходим на страницу материалов
        driver.get(f'{live_server.url}/admin/warehouse/material/')

        # Выбираем все материалы
        driver.find_element(By.ID, 'action-toggle').click()

        # Выбираем действие "Экспортировать в CSV"
        select = driver.find_element(By.NAME, 'action')
        for option in select.find_elements(By.TAG_NAME, 'option'):
            if 'Экспортировать выбранные материалы в CSV' in option.text:
                option.click()
                break

        # Выполняем действие
        driver.find_element(By.NAME, 'index').click()

        # Ждем загрузки файла
        import time
        time.sleep(2)  # Даем время на загрузку файла

        # Проверяем, что файл был загружен
        download_dir = os.path.join(os.getcwd(), 'test_downloads')
        files = os.listdir(download_dir)
        assert len(files) == 1
        assert files[0].startswith('materials_') and files[0].endswith('.csv')

        # Проверяем содержимое файла
        with open(os.path.join(download_dir, files[0]), 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 3  # Заголовок + 2 материала
            assert rows[0] == ['Наименование', 'Категория', 'Описание', 'Единица измерения', 'Количество']
            assert 'Test Material 1' in rows[1]
            assert 'Test Material 2' in rows[2]
