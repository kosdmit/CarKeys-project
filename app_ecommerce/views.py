import telegram.error
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView

from app_ecommerce.forms import CustomerForm
from app_ecommerce.mixins import AddCallbackFormMixin
from app_ecommerce.models import Goods, Category, Order, Customer
from app_ecommerce.services import send_telegram_message, construct_message


# Create your views here.
class GoodsListView(AddCallbackFormMixin, ListView):
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


class OrderCreateView(View):
    def post(self, request, *args, **kwargs):
        try:
            obj_id = request.POST['obj_id']
            goods = Goods.objects.get(pk=obj_id)
        except Goods.DoesNotExist:
            raise Http404

        session_id = self.request.session.session_key
        if not session_id:
            self.request.session.create()
            session_id = self.request.session.session_key
        customer = Customer.objects.filter(session_id=session_id).first()
        if not customer:
            customer = Customer.objects.create(session_id=session_id)

        order = Order.objects.create(goods=goods, customer=customer)

        ordered_goods = self.request.session.get('ordered_goods')
        if ordered_goods:
            self.request.session['ordered_goods'].append(str(goods.pk))
            self.request.session.save()
        else:
            self.request.session['ordered_goods'] = [str(goods.pk)]

        message = construct_message(request=self.request, goods=goods)
        response = send_telegram_message(message)

        if customer.phone_number:
            response['next'] = 'success-modal'
        else:
            response['next'] = 'get-contacts-modal'

        return JsonResponse(response)

    def get(self, request, *args, **kwargs):
        raise Http404


class CustomerUpdateView(UpdateView):
    model = Customer
    fields = ['name', 'phone_number']

    def get_object(self, queryset=None):
        session_id = self.request.session.session_key
        if session_id:
            obj = Customer.objects.get(session_id=session_id)
        else:
            self.request.session.create()
            session_id = self.request.session.session_key
            obj = Customer.objects.create(session_id=session_id)

        return obj

    def form_valid(self, form):
        self.object = form.save()
        customer = {'name': self.object.name,
                    'phone_number': self.object.phone_number}
        self.request.session['customer'] = customer

        message = construct_message(request=self.request)
        response = send_telegram_message(message)

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META['HTTP_REFERER'] + '?modal_id=success-modal'


