# products/tests.py

from django.test import TestCase
from product.models import Category, Product
from decimal import Decimal
from django.test import Client
from django.urls import reverse


class CategoryModelTest(TestCase):

    def setUp(self):
        # Создаем тестовую категорию
        self.category = Category.objects.create(
            name="Электроника",
            description="Гаджеты и техника"
        )

    def test_category_creation(self):
        """Проверяет, что объект Category был успешно создан."""
        self.assertEqual(self.category.name, "Электроника")
        self.assertEqual(self.category.description, "Гаджеты и техника")

    def test_category_str_method(self):
        """Проверяет, что метод __str__ возвращает название категории."""
        self.assertEqual(str(self.category), "Электроника")


class ProductModelTest(TestCase):

    def setUp(self):
        # 1. Сначала создаем категорию, так как она нужна для товара
        self.category = Category.objects.create(name="Книги")

        # 2. Создаем тестовый товар
        self.product = Product.objects.create(
            name="Django for Beginners",
            description="Учебник по фреймворку Django.",
            price=Decimal('50.00'),
            stock=5,
            category=self.category # Привязываем товар к категории
        )

    def test_product_creation(self):
        """Проверяет, что товар был успешно создан с правильными атрибутами."""
        self.assertEqual(self.product.name, "Django for Beginners")
        self.assertEqual(self.product.price, Decimal('50.00'))
        self.assertEqual(self.product.stock, 5)
        # Проверяем связь с категорией
        self.assertEqual(self.product.category.name, "Книги")

    def test_product_str_method(self):
        """Проверяет, что метод __str__ возвращает название товара."""
        self.assertEqual(str(self.product), "Django for Beginners")

    def test_stock_availability(self):
        """Проверяет поведение запаса (stock)."""
        # Товар в наличии
        self.assertTrue(self.product.stock > 0)
        
        # Товар распродан (out of stock)
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.stock > 0)


class ProductViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.category_a = Category.objects.create(name="A")
        self.category_b = Category.objects.create(name="B")
        
        # Создаем несколько товаров
        self.product_1 = Product.objects.create(
            name="Товар 1",
            description="Детали 1",
            price=10.00,
            stock=10,
            category=self.category_a
        )
        self.product_2 = Product.objects.create(
            name="Товар 2",
            description="Детали 2",
            price=20.00,
            stock=5,
            category=self.category_b
        )
        
        # Предполагаемые URL-имена (из urls.py)
        self.list_url = reverse('product:product_list')
        self.detail_url = reverse('product:product_detail', args=[self.product_1.id])
        # Добавим тест на просмотр по категории, если он есть
        self.category_url = reverse('product:category_view', args=[self.category_a.id]) 


    def test_product_list_view_status_code(self):
        """Проверяет, что страница со списком товаров доступна."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_product_list_view_contains_all_products(self):
        """Проверяет, что страница списка содержит оба товара."""
        response = self.client.get(self.list_url)
        self.assertContains(response, "Товар 1")
        self.assertContains(response, "Товар 2")
        self.assertContains(response, self.category_a.name) # Проверяем, что отображается название категории

    def test_product_detail_view_status_code(self):
        """Проверяет, что страница с деталями товара доступна."""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view_correct_content(self):
        """Проверяет, что на странице деталей отображаются данные конкретного товара."""
        response = self.client.get(self.detail_url)
        self.assertContains(response, self.product_1.name)
        self.assertContains(response, self.product_1.description)
        self.assertNotContains(response, self.product_2.name) # Убеждаемся, что не видно другого товара
        
    def test_product_detail_view_404_on_invalid_id(self):
        """Проверяет, что при неверном ID товара возвращается 404."""
        # Ищем товар с ID, которого точно нет
        invalid_url = reverse('product:product_detail', args=[9999]) 
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
