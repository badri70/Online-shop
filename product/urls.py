from django.urls import path
from .views import HomePageView, ProductListView, ProductDetailView, CartListView, AddToCartView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='products'),
    path('products/category/<int:category_id>/', ProductListView.as_view(), name='products_category'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product'),
    path('cart/', CartListView.as_view(), name='cart_list'),
    path('add_to_cart/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart')
]