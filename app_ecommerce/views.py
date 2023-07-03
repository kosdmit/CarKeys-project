from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from app_ecommerce.models import Goods


# Create your views here.
class GoodsView(ListView):
    template_name = 'app_ecomerce/goods.html'
    model = Goods
    paginate_by = 9