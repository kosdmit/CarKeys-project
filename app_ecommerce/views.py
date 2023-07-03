from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from app_ecommerce.models import Goods, Category


# Create your views here.
class GoodsView(ListView):
    template_name = 'app_ecomerce/goods.html'
    model = Goods
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        top_level_categories = Category.objects.filter(parent__isnull=True)
        context['top_level_categories'] = top_level_categories

        return context

    def get_queryset(self):
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                category_object = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                raise Http404
            query_set = category_object.get_goods()
            return query_set
        else:
            return super().get_queryset()