from django.urls import reverse_lazy
from django.views.generic import TemplateView

from app_ecommerce.mixins import AddCustomerFormMixin, AddPriceListDataMixin
from app_ecommerce.models import Goods


# Create your views here.
class MainView(AddPriceListDataMixin, AddCustomerFormMixin, TemplateView):
    template_name = 'app_landing/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['goods_link'] = reverse_lazy('goods')
        goods_list = Goods.objects.filter(is_active=True, is_available=True)[:4]
        context['goods_list'] = goods_list
        context['page_obj'] = goods_list

        return context

