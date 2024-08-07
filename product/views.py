from typing import Any
import logging
import stripe
from django.db.models.query import QuerySet
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView, View
from .models import Category, Product, Cart, CartItem


stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


# Create your views here.
class HomePageView(TemplateView):
    template_name = 'product/home_page.html'


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'product/products.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        if category_id:
            queryset = Product.objects.filter(category=category_id)
        return queryset


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'product/detail.html'
    context_object_name = 'product'


class AddToCartView(LoginRequiredMixin, View):
    def get(self, request, product_id):
        cart, created = Cart.objects.get_or_create(user=request.user)
        product = get_object_or_404(Product, id=product_id)
        cart_item, created = CartItem.objects.get_or_create(product=product, cart=cart)

        if not created:
            cart_item.quantity += 1
            cart_item.save()
        else:
            cart_item.save()
        
        return redirect('cart_list')

class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'product/cart.html'
    context_object_name = 'cart'

    def get_queryset(self) -> QuerySet[Any]:
        return Cart.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context['cart'] = Cart.objects.get(user=self.request.user)
        return context


class CreateStripeCheckoutSessionView(View):
    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, user=request.user)
        line_items = []

        for cart_item in cart.cart_item.all():
            line_items.append({
                "price_data": {
                    "currency": "eur",
                    "unit_amount": int(cart_item.product.price * 100),
                    "product_data": {
                        "name": cart_item.product.name,
                        "description": cart_item.product.description,
                        "images": [
                            f"{settings.BACKEND_DOMAIN}{cart_item.product.image.url}"
                        ],
                    },
                },
                "quantity": cart_item.quantity
            })
        
        logger.info(f"Line items: {line_items}")

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            metadata={"cart_id": cart.id},
            mode="payment",
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )

        logger.info(f"Checkout session created: {checkout_session}")

        return redirect(checkout_session.url)


class SuccessView(TemplateView):
    template_name = "product/success.html"


class CancelView(TemplateView):
    template_name = "product/cancel.html"


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request, format=None):
        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        logger.info(f"Received webhook: {payload}")

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
            logger.info(f"Webhook event received: {event['type']}")
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            pass
            

        return HttpResponse(status=200)
    

