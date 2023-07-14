import telegram.error
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView

from app_ecommerce.models import Goods, Category
from app_ecommerce.services import send_telegram_message, construct_message


# Create your views here.
class GoodsListView(ListView):
    template_name = 'app_ecomerce/goods.html'
    model = Goods
    paginate_by = 9

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.category_object = None

    def dispatch(self, request, *args, **kwargs):
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                self.category_object = Category.objects.get(slug=category_slug)
            except Category.DoesNotExist:
                raise Http404

        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        top_level_categories = Category.objects.filter(parent__isnull=True)
        context['top_level_categories'] = top_level_categories

        # Get breadcrumbs
        breadcrumbs = []
        if self.category_object and self.category_object.parent:
            breadcrumbs.append([
                self.category_object.parent.title,
                reverse_lazy('goods') + '?category=' + self.category_object.parent.slug
            ])

        if self.category_object:
            breadcrumbs.append([self.category_object.title, ''])
        else:
            breadcrumbs.append(['Все категории', ''])

        context['breadcrumbs'] = breadcrumbs

        return context

    def get_queryset(self):
        if self.category_object:
            query_set = self.category_object.get_goods()
            query_set = query_set.filter(is_active=True)
            return query_set
        else:
            query_set = super().get_queryset()
            query_set = query_set.filter(is_active=True)
            return query_set


class SendMessageView(View):
    def post(self, request, *args, **kwargs):
        data = request.POST
        message = construct_message(data)
        response = send_telegram_message(message)

        return JsonResponse(response)

    def get(self, request, *args, **kwargs):
        raise Http404

