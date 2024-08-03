from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


# class Order(models.Model):
#     STATUS_CHOICES = [
#         ('processing', 'В обработке'),
#         ('shipped', 'Отправлен'),
#         ('delivered', 'Доставлен'),
#         ('cancelled', 'Отменен'),
#     ]
    
#     user = models.ForeignKey(to=User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='processing')

#     def __str__(self):
#         return f'Order {self.id} by {self.user.username}'
    

# class OrderItem(models.Model):
#     order = models.ForeignKey(to=Order, on_delete=models.CASCADE, related_name='order_item')
#     product = models.ForeignKey(to=Product, on_delete=models.CASCADE, related_name='order_product')
#     quantity = models.PositiveIntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)

#     def __str__(self):
#         return f'Order: {self.id}-{self.quantity}-{self.price}'


# class Cart(models.Model):
#     user = models.ForeignKey(to=User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f'Cart {self.id} by {self.user.username}'


    