from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class GoodsView(TemplateView):
    template_name = 'app_ecomerce/goods.html'