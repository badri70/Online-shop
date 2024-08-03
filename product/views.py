from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DetailView
from .models import Category, Product

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
    