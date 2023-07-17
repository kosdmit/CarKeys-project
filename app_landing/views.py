from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from app_ecommerce.mixins import AddCallbackFormMixin, AddPriceListDataMixin
from app_ecommerce.models import Goods


# Create your views here.
class MainView(AddPriceListDataMixin, AddCallbackFormMixin, TemplateView):
    template_name = 'app_landing/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['goods_link'] = reverse_lazy('goods')
        goods_list = Goods.objects.all()[:3]
        context['goods_list'] = goods_list
        context['page_obj'] = goods_list

        return context

