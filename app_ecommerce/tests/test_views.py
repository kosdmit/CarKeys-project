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


    @pytest.fixture()
    def check_goods(self, request):
        self.top_level_categories = mixer.cycle(5).blend(Category, parent=None)

        for category in self.top_level_categories:
            mixer.cycle(3).blend(Category, parent=category)

        self.available_goods = mixer.cycle(10).blend(Goods, parent=mixer.select, is_active=True, count=1)
        self.unavailable_goods = mixer.cycle(2).blend(Goods, parent=mixer.select, is_active=True, count=0)
        self.disabled_goods = mixer.blend(Goods, parent=mixer.select, is_active=False)

        self.selected_top_level_category = mixer.blend(Category,
                                                       parent=None,
                                                       title='Selected top level category')
        self.selected_second_level_category = mixer.blend(Category,
                                                          parent=self.selected_top_level_category,
                                                          title='Selected second level category')

        self.top_level_categories_count = len(self.top_level_categories) + 1
        self.available_goods_count = len(self.available_goods)
        self.unavailable_goods_count = len(self.unavailable_goods)
        self.displayed_goods_count = self.available_goods_count + self.unavailable_goods_count

        def check_top_level_categories_in_context():
            assert 'top_level_categories' in self.context
            assert len(self.context['top_level_categories']) == self.top_level_categories_count
            assert self.selected_top_level_category in self.context['top_level_categories']
        request.addfinalizer(check_top_level_categories_in_context)

        def check_goods_in_context():
            if self.displayed_goods_count >= self.paginate_by:
                assert len(self.context['page_obj']) == self.paginate_by
            else:
                assert len(self.context['page_obj']) == self.displayed_goods_count

            assert self.context['paginator'].count == self.displayed_goods_count
        request.addfinalizer(check_goods_in_context)

        def check_goods_ordering():
            for i in range(self.available_goods_count):
                assert self.context['paginator'].object_list[i].is_available is True
            for i in range(self.available_goods_count, self.displayed_goods_count):
                assert self.context['paginator'].object_list[i].is_available is False
        request.addfinalizer(check_goods_ordering)


    @pytest.fixture()
    def check_services(self, request):
        self.active_services = mixer.cycle(3).blend(Service, is_active=True)
        self.disabled_services = mixer.blend(Service, is_active=False)

        def check_services_count_in_context():
            assert len(self.context['price_list']) == len(self.active_services)
        request.addfinalizer(check_services_count_in_context)


    def test_goods_list_view_no_category(self, check_goods, check_services):
        response = self.client.get(reverse('goods'))
        self.context = response.context_data

        assert response.status_code == 200

        # check category in breadcrumbs
        assert len(self.context['breadcrumbs']) == 1
        assert self.context['breadcrumbs'][0][0] == _('All categories')
        assert self.context['breadcrumbs'][0][1] is None


    def test_goods_list_view_with_top_level_category(self, check_goods, check_services):
        selected_available_goods = mixer.cycle(3).blend(Goods,
                                                        parent=self.selected_top_level_category,
                                                        is_active=True,
                                                        count=1)
        self.available_goods_count = len(selected_available_goods)

        selected_unavailable_goods = mixer.cycle(2).blend(Goods,
                                                          parent=self.selected_top_level_category,
                                                          is_active=True,
                                                          count=0)
        self.unavailable_goods_count = len(selected_unavailable_goods)
        self.displayed_goods_count = self.available_goods_count + self.unavailable_goods_count

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


    def test_goods_list_view_with_second_level_category(self, check_goods, check_services):
        top_level_goods = mixer.blend(Goods,
                                      parent=self.selected_top_level_category,
                                      is_active=True,
                                      count=1)

        selected_available_goods = mixer.cycle(3).blend(Goods,
                                                        parent=self.selected_second_level_category,
                                                        is_active=True,
                                                        count=1)
        self.available_goods_count = len(selected_available_goods)

        selected_unavailable_goods = mixer.cycle(2).blend(Goods,
                                                          parent=self.selected_second_level_category,
                                                          is_active=True,
                                                          count=0)
        self.unavailable_goods_count = len(selected_unavailable_goods)
        self.displayed_goods_count = self.available_goods_count + self.unavailable_goods_count

        selected_disabled_goods = mixer.cycle(1).blend(Goods,
                                                       parent=self.selected_second_level_category,
                                                       is_active=False,
                                                       count=1)

        response = self.client.get(reverse('goods'), {'category': self.selected_second_level_category.slug})
        self.context = response.context_data

        assert response.status_code == 200

        # check category in breadcrumbs
        assert len(self.context['breadcrumbs']) == 2
        assert self.context['breadcrumbs'][1][0] == self.selected_second_level_category.title
        assert self.context['breadcrumbs'][1][1] is None
        assert self.context['breadcrumbs'][0][0] == self.selected_top_level_category.title
        assert self.context['breadcrumbs'][0][1] == reverse('goods') + f'?category={self.selected_top_level_category.slug}'


    def test_goods_list_view_with_invalid_category(self):
        response = self.client.get(reverse('goods'), {'category': 'non-existent-category'})
        assert response.status_code == 404


    def test_customer_form_with_session_data(self):
        session = self.client.session
        session['customer_form_data'] = {'name': 'test name',
                                         'phone_number': '+79277777777'}
        session.save()

        response = self.client.get(reverse('goods'))
        customer_form = response.context_data['customer_form']

        assert 'customer_form' in response.context_data
        assert isinstance(customer_form, CustomerForm)
        assert customer_form.is_bound  # This checks that the form was bound with data
        assert customer_form.data['name'] == session['customer_form_data']['name']
        assert customer_form.data['phone_number'] == session['customer_form_data']['phone_number']

        assert 'message_form' in response.context_data
        assert isinstance(response.context_data['message_form'], MessageForm)
        assert not response.context_data['message_form'].is_bound


    def test_customer_form_with_customer_in_db(self):
        customer = mixer.blend(Customer,
                               session_id=self.client.session.session_key,
                               name='test user',
                               phone_number='+79277777777')

        response = self.client.get(reverse('goods'))

        assert 'customer_form' in response.context_data
        assert isinstance(response.context_data['customer_form'], CustomerForm)
        assert response.context_data['customer_form'].is_bound
        assert 'message_form' in response.context_data
        assert isinstance(response.context_data['message_form'], MessageForm)

