"""
URL configuration for carkeys_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from app_ecommerce.views import GoodsListView, OrderCreateView, \
    CustomerUpdateView
from app_landing.views import MainView

urlpatterns = [
    path('', GoodsListView.as_view(), name='goods'),
    path('order_create/', OrderCreateView.as_view(), name='order_create'),
    path('customer_update/', CustomerUpdateView.as_view(), name='customer_update'),
]
