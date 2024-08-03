from django.urls import path
from .views import HomePageView, ProductListView, ProductDetailView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='products'),
    path('products/category/<int:category_id>/', ProductListView.as_view(), name='products_category'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product'),
]