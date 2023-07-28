import pytest
from django.test import Client
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mixer.backend.django import mixer

from app_ecommerce.forms import CustomerForm, MessageForm
from app_ecommerce.models import Category, Goods, Service, Customer
from app_ecommerce.views import GoodsListView


# Create your tests here.
@pytest.mark.django_db
class TestGoodsListView:
    def setup(self):
        self.client = Client()
        self.paginate_by = GoodsListView.paginate_by

        self.test_data = {'customer_name': 'Leonid',
                          'customer_phone_number': '+79277777777',
                          'top_level_category_title': 'Top category',
                          'second_level_category_title': 'Second category'}

    @pytest.fixture()
    def prepare_goods(self, request):
        self.top_level_categories = mixer.cycle(5).blend(Category, parent=None)
        self.second_level_categories = [mixer.cycle(3).blend(Category, parent=cat) for cat in self.top_level_categories]

        self.available_goods = mixer.cycle(10).blend(Goods, parent=mixer.select, is_active=True, count=1)
        self.unavailable_goods = mixer.cycle(2).blend(Goods, parent=mixer.select, is_active=True, count=0)
        self.disabled_goods = mixer.blend(Goods, parent=mixer.select, is_active=False)

        self.selected_top_level_category = mixer.blend(Category, parent=None, title=self.test_data['top_level_category_title'])
        self.top_level_categories.append(self.selected_top_level_category)

    def check_top_level_categories_in_context(self):
        assert 'top_level_categories' in self.context
        assert len(self.context['top_level_categories']) == len(self.top_level_categories)
        assert self.selected_top_level_category in self.context['top_level_categories']

    def check_goods_in_context(self):
        displayed_goods_count = len(self.available_goods) + len(self.unavailable_goods)

        if displayed_goods_count >= self.paginate_by:
            assert len(self.context['page_obj']) == self.paginate_by
        else:
            assert len(self.context['page_obj']) == displayed_goods_count

        assert self.context['paginator'].count == displayed_goods_count

    def check_goods_ordering(self):
        available_goods_count = len(self.available_goods)
        displayed_goods_count = len(self.available_goods) + len(self.unavailable_goods)

        for i in range(available_goods_count):
            assert self.context['paginator'].object_list[i].is_available is True
        for i in range(available_goods_count, displayed_goods_count):
            assert self.context['paginator'].object_list[i].is_available is False

    @pytest.fixture()
    def prepare_services(self, request):
        self.active_services = mixer.cycle(3).blend(Service, is_active=True)
        self.disabled_services = mixer.blend(Service, is_active=False)

    def check_services_count_in_context(self):
        assert len(self.context['price_list']) == len(self.active_services)

    def check_message_form_in_context(self):
        assert 'message_form' in self.context
        assert isinstance(self.context['message_form'], MessageForm)
        assert not self.context['message_form'].is_bound

    def test_goods_list_view_no_category(self, prepare_goods, prepare_services):
        response = self.client.get(reverse('goods'))
        self.context = response.context_data

        assert response.status_code == 200

        # check category in breadcrumbs
        assert len(self.context['breadcrumbs']) == 1
        assert self.context['breadcrumbs'][0][0] == _('All categories')
        assert self.context['breadcrumbs'][0][1] is None

        self.check_top_level_categories_in_context()
        self.check_goods_in_context()
        self.check_goods_ordering()

        self.check_services_count_in_context()
        self.check_message_form_in_context()

    def test_goods_list_view_with_top_level_category(self, prepare_goods, prepare_services):
        self.available_goods = mixer.cycle(3).blend(Goods,
                                                    parent=self.selected_top_level_category,
                                                    is_active=True,
                                                    count=1)

        self.unavailable_goods = mixer.cycle(2).blend(Goods,
                                                      parent=self.selected_top_level_category,
                                                      is_active=True,
                                                      count=0)

        selected_disabled_goods = mixer.cycle(1).blend(Goods,
                                                       parent=self.selected_top_level_category,
                                                       is_active=False,
                                                       count=1)

        response = self.client.get(
            reverse('goods'),
            {'category': self.selected_top_level_category.slug}
        )
        self.context = response.context_data

        assert response.status_code == 200

        # check category in breadcrumbs
        assert len(self.context['breadcrumbs']) == 1
        assert self.context['breadcrumbs'][0][0] == self.selected_top_level_category.title
        assert self.context['breadcrumbs'][0][1] is None

        self.check_top_level_categories_in_context()
        self.check_goods_in_context()
        self.check_goods_ordering()

        self.check_services_count_in_context()
        self.check_message_form_in_context()

    def test_goods_list_view_with_second_level_category(self, prepare_goods, prepare_services):
        selected_second_level_category = mixer.blend(Category,
                                                          parent=self.selected_top_level_category,
                                                          title=self.test_data['second_level_category_title'])

        top_level_goods = mixer.blend(Goods,
                                      parent=self.selected_top_level_category,
                                      is_active=True,
                                      count=1)

        self.available_goods = mixer.cycle(3).blend(Goods,
                                                    parent=selected_second_level_category,
                                                    is_active=True,
                                                    count=1)

        self.unavailable_goods = mixer.cycle(2).blend(Goods,
                                                      parent=selected_second_level_category,
                                                      is_active=True,
                                                      count=0)

        selected_disabled_goods = mixer.cycle(1).blend(Goods,
                                                       parent=selected_second_level_category,
                                                       is_active=False,
                                                       count=1)

        response = self.client.get(reverse('goods'), {'category': selected_second_level_category.slug})
        self.context = response.context_data

        assert response.status_code == 200

        # check category in breadcrumbs
        assert len(self.context['breadcrumbs']) == 2
        assert self.context['breadcrumbs'][1][0] == selected_second_level_category.title
        assert self.context['breadcrumbs'][1][1] is None
        assert self.context['breadcrumbs'][0][0] == self.selected_top_level_category.title
        assert self.context['breadcrumbs'][0][1] == reverse('goods') + f'?category={self.selected_top_level_category.slug}'

        self.check_top_level_categories_in_context()
        self.check_goods_in_context()
        self.check_goods_ordering()

        self.check_services_count_in_context()
        self.check_message_form_in_context()

    def test_goods_list_view_with_invalid_category(self):
        response = self.client.get(reverse('goods'), {'category': 'non-existent-category'})
        assert response.status_code == 404

    def test_customer_form_with_session_data(self):
        session = self.client.session
        session['customer_form_data'] = {'name': self.test_data['customer_name'],
                                         'phone_number': self.test_data['customer_phone_number']}
        session.save()

        response = self.client.get(reverse('goods'))
        self.context = response.context_data

        assert 'customer_form' in response.context_data
        assert isinstance(self.context['customer_form'], CustomerForm)
        assert self.context['customer_form'].is_bound  # This checks that the form was bound with data
        assert self.context['customer_form'].data['name'] == self.test_data['customer_name']
        assert self.context['customer_form'].data['phone_number'] == self.test_data['customer_phone_number']

        self.check_message_form_in_context()

    def test_customer_form_with_customer_in_db(self):
        customer = mixer.blend(Customer,
                               session_id=self.client.session.session_key,
                               name=self.test_data['customer_name'],
                               phone_number=self.test_data['customer_phone_number'])

        response = self.client.get(reverse('goods'))
        self.context = response.context_data

        assert 'customer_form' in self.context
        assert isinstance(self.context['customer_form'], CustomerForm)
        assert self.context['customer_form'].instance.name == self.test_data['customer_name']
        assert self.context['customer_form'].instance.phone_number == self.test_data['customer_phone_number']

    def test_add_customer_form_mixin_with_no_customer(self):
        response = self.client.get(reverse('goods'))
        self.context = response.context_data

        assert 'customer_form' in self.context
        assert isinstance(self.context['customer_form'], CustomerForm)
        assert not self.context['customer_form'].is_bound  # This checks that the form was not bound with data


