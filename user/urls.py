from django.urls import path
from .views import SingUpView, login_user


urlpatterns = [
    path('register/', SingUpView.as_view(), name='register'),
    path('login/', login_user, name='login'),
]