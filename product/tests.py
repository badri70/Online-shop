# products/tests.py

from django.test import TestCase
from products.models import Category, Product
from decimal import Decimal

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


