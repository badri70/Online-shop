from typing import Any
import stripe
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView, DetailView, View
from .models import Category, Product, Cart, CartItem, Order, OrderItem, Payment


stripe.api_key = settings.STRIPE_SECRET_KEY


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


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'product/order.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


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
        

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            metadata={"cart_id": cart.id, "user_id": request.user.id},
            mode="payment",
            success_url=settings.PAYMENT_SUCCESS_URL,
            cancel_url=settings.PAYMENT_CANCEL_URL,
        )


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


        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            user = User.objects.get(id=session["metadata"]["user_id"])
            amount = session["amount_total"]/100
            customer_email = session["customer_details"]["email"]
            
            order = Order.objects.create(user=user, total_price=amount)
            cart = Cart.objects.get(id=session["metadata"]["cart_id"])

            for cart_item in cart.cart_item.all():
                OrderItem.objects.create(
                    product = cart_item.product,
                    quantity = cart_item.quantity,
                    price = cart_item.product.price,
                    order = order
                )
            
            cart.delete()

            send_mail(
                subject="Here is your product",
                message=f"Thanks for your purchase. The URL is: http://localhost:8000/products/",
                recipient_list=[customer_email],
                from_email="test@gmail.com",
                fail_silently=False,
            )

            Payment.objects.create(
                email = customer_email,
                order = order,
                amount = amount
            )

        return HttpResponse(status=200)
    

