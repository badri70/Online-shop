from django.urls import path
from .views import (
    CancelView, 
    HomePageView, 
    ProductListView, 
    ProductDetailView, 
    CartListView, 
    AddToCartView, 
    CreateStripeCheckoutSessionView, 
    SuccessView,
    StripeWebhookView,
    OrderListView
)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('products/', ProductListView.as_view(), name='products'),
    path('products/category/<int:category_id>/', ProductListView.as_view(), name='products_category'),
    path('products/<int:pk>/', ProductDetailView.as_view(), name='product'),
    path('cart/', CartListView.as_view(), name='cart_list'),
    path('orders/', OrderListView.as_view(), name='order_list'),
    path('add_to_cart/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path(
        "create-checkout-session/<int:pk>/",
        CreateStripeCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("success/", SuccessView.as_view(), name="success"),
    path("cancel/", CancelView.as_view(), name="cancel"),
    path("webhooks/stripe/", StripeWebhookView.as_view(), name="stripe-webhook"),
]