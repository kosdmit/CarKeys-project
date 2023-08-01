import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.test import RequestFactory
from django.urls import reverse
from django.utils.http import urlencode
from mixer.backend.django import mixer

from app_ecommerce.models import Goods, Customer, Order
from app_ecommerce.services import construct_message, MESSAGE_LINES
from app_ecommerce.tests.data import TEST_DATA
from app_ecommerce.tests.mixins import CreateTestObjectsMixin
from carkeys_project import settings


@pytest.mark.django_db
class TestConstructMessage(CreateTestObjectsMixin):

    def setup(self):
        self.factory = RequestFactory()
        self.data = {'name': TEST_DATA['customer_name'],
                     'phone_number': TEST_DATA['customer_phone_number'],
                     'text': TEST_DATA['customer_message']}

    @staticmethod
    def get_session(request):
        middleware = SessionMiddleware(lambda x: None)
        middleware.process_request(request)
        request.session.save()

    @staticmethod
    def check_customer_input(message):
        assert TEST_DATA['customer_name'] in message
        assert TEST_DATA['customer_phone_number'] in message
        assert TEST_DATA['customer_message'] in message

    @staticmethod
    def check_goods_properties(order, message):
        assert order.goods.title in message
        assert str(order.goods.count) in message
        assert str(order.goods.price) in message

    @staticmethod
    def check_service_properties(order, message):
        assert order.service.title in message
        assert str(order.service.price) in message

    @staticmethod
    def check_link(order, message):
        assert str(order.goods.pk) in message
        assert 'modal_id=detail-view-modal-' in message
        assert reverse('goods') in message
        assert any(host in message for host in settings.ALLOWED_HOSTS)


    def test_callback_request_without_ordered_objects(self):
        request = self.factory.post(
            'customer_update',
            data=urlencode(self.data),
            content_type='application/x-www-form-urlencoded',
        )
        self.get_session(request)
        request.META = {'HTTP_REFERER': reverse('goods') + '?modal_id=callback-modal'}

        customer = Customer.objects.create(session_id=request.session.session_key,
                                           name=TEST_DATA['customer_name'],
                                           phone_number=TEST_DATA['customer_phone_number'])

        message = construct_message(request)

        self.check_customer_input(message)
        assert MESSAGE_LINES['callback_order'] in message
        assert MESSAGE_LINES['no_obj'] in message

        print(message)

    def test_callback_request_with_ordered_goods(self, prepare_goods):
        request = self.factory.post(
            'customer_update',
            data=urlencode(self.data),
            content_type='application/x-www-form-urlencoded',
        )
        self.get_session(request)
        request.META = {'HTTP_REFERER': reverse('goods') + '?modal_id=callback-modal'}

        customer = Customer.objects.create(session_id=request.session.session_key,
                                           name=self.data['name'],
                                           phone_number=self.data['phone_number'])
        orders = mixer.cycle(5).blend(Order, goods=mixer.select, customer=customer, service=None)
        order = Order.objects.filter(customer=customer).last()

        message = construct_message(request)

        self.check_customer_input(message)
        self.check_goods_properties(order, message)
        self.check_link(order, message)
        assert MESSAGE_LINES['callback_order'] in message

        print(message)

    def test_callback_request_with_ordered_service(self, prepare_services):
        request = self.factory.post(
            'customer_update',
            data=urlencode(self.data),
            content_type='application/x-www-form-urlencoded',
        )
        self.get_session(request)
        request.META = {'HTTP_REFERER': reverse('main') + '?modal_id=callback-modal'}

        customer = Customer.objects.create(session_id=request.session.session_key,
                                           name=self.data['name'],
                                           phone_number=self.data['phone_number'])
        orders = mixer.cycle(5).blend(Order, service=mixer.select, customer=customer, goods=None)
        order = Order.objects.filter(customer=customer).last()

        message = construct_message(request)

        self.check_customer_input(message)
        self.check_service_properties(order, message)
        assert MESSAGE_LINES['callback_order'] in message

        print(message)

    def test_goods_ordering_with_new_customer(self, prepare_goods):
        goods = Goods.objects.last()

        request = self.factory.post(
            'order_create',
            data=urlencode({'obj_id': goods.pk,
                            'obj_type': type(goods)}),
            content_type='application/x-www-form-urlencoded',
        )
        self.get_session(request)
        request.META = {'HTTP_REFERER': reverse('goods') + '?modal_id=detail_view-modal-' + goods.slug}

        customer = Customer.objects.create(session_id=request.session.session_key)
        order = Order.objects.create(customer=customer, goods=goods)

        message = construct_message(request)

        self.check_goods_properties(order, message)
        assert MESSAGE_LINES['no_phone_number'] in message

        print(message)

    def test_add_contacts_to_order(self, prepare_goods):
        goods = Goods.objects.last()

        request = self.factory.post(
            'customer_update',
            data=urlencode(self.data),
            content_type='application/x-www-form-urlencoded',
        )
        self.get_session(request)
        request.META = {'HTTP_REFERER': reverse('goods') + '?modal_id=get_contacts_modal'}

        customer = Customer.objects.create(session_id=request.session.session_key,
                                           name=self.data['name'],
                                           phone_number=self.data['phone_number'])
        order = Order.objects.create(customer=customer, goods=goods)

        message = construct_message(request)

        self.check_customer_input(message)
        self.check_goods_properties(order, message)
        self.check_link(order, message)
        assert not MESSAGE_LINES['no_phone_number'] in message

        print(message)

    def test_goods_ordering_with_existing_customer(self, prepare_goods):
        goods = Goods.objects.last()

        request = self.factory.post(
            'order_create',
            data=urlencode({'obj_id': goods.pk,
                            'obj_type': type(goods)}),
            content_type='application/x-www-form-urlencoded',
        )
        self.get_session(request)
        request.META = {'HTTP_REFERER': reverse('goods') + '?modal_id=detail_view-modal-' + goods.slug}

        customer = Customer.objects.create(session_id=request.session.session_key,
                                           name=self.data['name'],
                                           phone_number=self.data['phone_number'])
        order = Order.objects.create(customer=customer, goods=goods)

        message = construct_message(request)

        assert TEST_DATA['customer_name'] in message
        assert TEST_DATA['customer_phone_number'] in message

        self.check_goods_properties(order, message)
        self.check_link(order, message)
        assert not MESSAGE_LINES['no_phone_number'] in message

        print(message)