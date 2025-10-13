from django.test import TestCase
from product.models import Category, Product
from decimal import Decimal
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User 


class CategoryModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Электроника",
            description="Гаджеты и техника"
        )

    def test_category_creation(self):
        self.assertEqual(self.category.name, "Электроника")
        self.assertEqual(self.category.description, "Гаджеты и техника")

    def test_category_str_method(self):
        self.assertEqual(str(self.category), "Электроника")


class ProductModelTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(name="Книги")

        self.product = Product.objects.create(
            name="Django for Beginners",
            description="Учебник по фреймворку Django.",
            price=Decimal('50.00'),
            stock=5,
            category=self.category 
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Django for Beginners")
        self.assertEqual(self.product.price, Decimal('50.00'))
        self.assertEqual(self.product.stock, 5)
        self.assertEqual(self.product.category.name, "Книги")

    def test_product_str_method(self):
        self.assertEqual(str(self.product), "Django for Beginners")

    def test_stock_availability(self):
        
        self.assertTrue(self.product.stock > 0)
        
        self.product.stock = 0
        self.product.save()
        self.assertFalse(self.product.stock > 0)
        

class ProductViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123') 
        self.client.login(username='testuser', password='password123') 
        
        self.category_a = Category.objects.create(name="A")
        self.category_b = Category.objects.create(name="B")
        
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
        
        self.list_url = reverse('products') 
        self.detail_url = reverse('product', args=[self.product_1.id]) 
        self.category_url = reverse('products_category', args=[self.category_a.id]) 
        
        self.invalid_detail_url = reverse('product', args=[9999])

    def test_product_list_view_status_code(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view_404_on_invalid_id(self):
        response = self.client.get(self.invalid_detail_url)
        self.assertEqual(response.status_code, 404)
        
    def test_product_list_view_by_category(self):
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.product_1.name)
        self.assertNotContains(response, self.product_2.name)
