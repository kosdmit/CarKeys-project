import json
from unittest.mock import patch

import pytest
from django.test import Client
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mixer.backend.django import mixer

from app_ecommerce.forms import CustomerForm, MessageForm
from app_ecommerce.models import Category, Goods, Service, Customer, Order, \
    Message, Contact
from app_ecommerce.tests.data import TEST_DATA
from app_ecommerce.tests.mixins import CreateTestObjectsMixin
from app_ecommerce.tests.mocks import mock_construct_message, \
    mock_send_telegram_message
from app_ecommerce.views import GoodsListView


# Create your tests here.
@pytest.mark.django_db
class TestGoodsListView(CreateTestObjectsMixin):
    def setup(self):
        self.client = Client()
        self.paginate_by = GoodsListView.paginate_by

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
                                                     title=TEST_DATA['second_level_category_title'])

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
        session['customer_form_data'] = {'name': TEST_DATA['customer_name'],
                                         'phone_number': TEST_DATA['customer_phone_number']}
        session.save()

        response = self.client.get(reverse('goods'))
        self.context = response.context_data

        assert 'customer_form' in response.context_data
        assert isinstance(self.context['customer_form'], CustomerForm)
        assert self.context['customer_form'].is_bound  # This checks that the form was bound with data
        assert self.context['customer_form'].data['name'] == TEST_DATA['customer_name']
        assert self.context['customer_form'].data['phone_number'] == TEST_DATA['customer_phone_number']

        self.check_message_form_in_context()

    def test_customer_form_with_customer_in_db(self):
        customer = mixer.blend(Customer,
                               session_id=self.client.session.session_key,
                               name=TEST_DATA['customer_name'],
                               phone_number=TEST_DATA['customer_phone_number'])

        response = self.client.get(reverse('goods'))
        self.context = response.context_data

        assert 'customer_form' in self.context
        assert isinstance(self.context['customer_form'], CustomerForm)
        assert self.context['customer_form'].instance.name == TEST_DATA['customer_name']
        assert self.context['customer_form'].instance.phone_number == TEST_DATA['customer_phone_number']

    def test_add_customer_form_mixin_with_no_customer(self):
        response = self.client.get(reverse('goods'))
        self.context = response.context_data

        assert 'customer_form' in self.context
        assert isinstance(self.context['customer_form'], CustomerForm)
        assert not self.context['customer_form'].is_bound  # This checks that the form was not bound with data

    def test_post_method(self):
        response = self.client.post(reverse('goods'))
        assert response.status_code == 405


@pytest.mark.django_db
class TestOrderCreateView:
    def setup(self):
        self.client = Client()

    @pytest.fixture()
    def prepare_objects(self):
        self.displayed_goods = mixer.cycle(3).blend(Goods, is_active=True)
        self.disabled_goods = mixer.cycle(2).blend(Goods, is_active=False)
        self.active_services = mixer.cycle(2).blend(Service, is_active=True)
        self.disabled_services = mixer.cycle(1).blend(Service, is_active=False)

    @patch('app_ecommerce.views.construct_message', new=mock_construct_message)
    @patch('app_ecommerce.views.send_telegram_message', new=mock_send_telegram_message)
    def test_post_correct_data_with_new_customer(self, prepare_objects):
        selected_obj = self.displayed_goods[0]

        response = self.client.post(reverse('order_create'), data={'obj_id': selected_obj.pk, 'obj_type': type(selected_obj).__name__})
        session_id = self.client.session.session_key
        customer = Customer.objects.filter(session_id=session_id).first()
        order = Order.objects.filter(customer=customer, goods=selected_obj).first()

        assert response.status_code == 200

        assert customer
        assert order
        assert str(selected_obj.pk) in self.client.session['ordered_goods']
        assert json.loads(response.content.decode())['next'] == 'get-contacts-modal'

    @patch('app_ecommerce.views.construct_message', new=mock_construct_message)
    @patch('app_ecommerce.views.send_telegram_message', new=mock_send_telegram_message)
    def test_post_correct_data_view_with_existing_customer(self, prepare_objects):
        selected_obj = self.displayed_goods[0]
        session_id = self.client.session.session_key
        customer = Customer.objects.create(session_id=session_id,
                                           name=TEST_DATA['customer_name'],
                                           phone_number=TEST_DATA['customer_phone_number'])
        ordered_goods = [str(goods.pk) for goods in self.displayed_goods if goods != selected_obj]
        session = self.client.session
        session['ordered_goods'] = ordered_goods
        session.save()

        response = self.client.post(reverse('order_create'), data={'obj_id': selected_obj.pk, 'obj_type': type(selected_obj).__name__})

        assert response.status_code == 200

        assert Order.objects.filter(goods=selected_obj, customer=customer).exists()
        assert str(selected_obj.pk) in self.client.session['ordered_goods']
        assert set([str(goods.pk) for goods in self.displayed_goods]) == set(self.client.session['ordered_goods'])
        assert json.loads(response.content.decode())['next'] == 'success-modal'

    def test_post_invalid_data(self, prepare_objects):
        selected_obj = self.displayed_goods[0]
        response = self.client.post(reverse('order_create'), data={'obj_id': selected_obj.pk,
                                                                   'obj_type': 'unexpectet_type'})

        assert response.status_code == 404

    def test_get_method(self):
        response = self.client.get(reverse('order_create'))

        assert response.status_code == 404


@pytest.mark.django_db
class TestCustomerUpdateView:
    def setup(self):
        self.client = Client()

    def check_response(self):
        assert self.response.status_code == 302
        assert 'modal_id=success-modal' in self.response.url

    def check_objects(self):
        assert Customer.objects.filter(name=TEST_DATA['customer_name'],
                                       phone_number=TEST_DATA['customer_phone_number']).exists()

        customer = Customer.objects.get(name=TEST_DATA['customer_name'],
                                        phone_number=TEST_DATA['customer_phone_number'])
        assert Message.objects.filter(customer=customer, text=TEST_DATA['customer_message']).exists()
        assert Contact.objects.filter(customer=customer,
                                      name=TEST_DATA['customer_name'],
                                      phone_number=TEST_DATA['customer_phone_number']).exists()

    @patch('app_ecommerce.views.construct_message', new=mock_construct_message)
    @patch('app_ecommerce.views.send_telegram_message', new=mock_send_telegram_message)
    def test_post_correct_data_with_new_customer(self):
        self.response = self.client.post(
            reverse('customer_update'),
            data={'name': TEST_DATA['customer_name'],
                  'phone_number': TEST_DATA['customer_phone_number'],
                  'text': TEST_DATA['customer_message']},
            HTTP_REFERER=reverse('goods')
        )

        self.check_response()
        self.check_objects()

    @patch('app_ecommerce.views.construct_message', new=mock_construct_message)
    @patch('app_ecommerce.views.send_telegram_message', new=mock_send_telegram_message)
    def test_post_correct_data_with_existing_customer(self):
        session_id = self.client.session.session_key
        customer = mixer.blend(Customer, session_id=session_id)

        self.response = self.client.post(
            reverse('customer_update'),
            data={'name': TEST_DATA['customer_name'],
                  'phone_number': TEST_DATA['customer_phone_number'],
                  'text': TEST_DATA['customer_message']},
            HTTP_REFERER=reverse('goods')
        )

        self.check_response()
        self.check_objects()

    @patch('app_ecommerce.views.construct_message', new=mock_construct_message)
    @patch('app_ecommerce.views.send_telegram_message', new=mock_send_telegram_message)
    def test_post_invalid_data_with_new_customer(self):
        self.response = self.client.post(
            reverse('customer_update'),
            data={'name': TEST_DATA['customer_name'],
                  'phone_number': 'invalid phone number',
                  'text': TEST_DATA['customer_message']},
            HTTP_REFERER=reverse('goods')
        )

        assert self.response.status_code == 302

        customer_form_data = self.response.client.session['customer_form_data']
        form = CustomerForm(customer_form_data)

        assert form.errors

        assert Customer.objects.filter(session_id=self.response.client.session.session_key).exists()
        assert not Customer.objects.filter(phone_number=TEST_DATA['customer_phone_number']).exists()
        assert not Message.objects.filter(text=TEST_DATA['customer_message']).exists()
        assert not Contact.objects.filter(phone_number=TEST_DATA['customer_phone_number']).exists()

    def test_get_method(self):
        response = self.client.get(reverse('order_create'))

        assert response.status_code == 404




