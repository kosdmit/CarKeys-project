import os
from textwrap import dedent
from urllib.parse import urlparse

import requests
from django.urls import reverse

from app_ecommerce.models import Goods, Customer
from carkeys_project import settings
from carkeys_project.settings import TELEGRAM_ADMIN_CHAT_ID


# TODO: improve algorithm for searching actual order for customer
# TODO: add functionality for bot, for example searching orders by customer


def construct_message(request, obj=None):
    session_id = request.session.session_key
    customer = Customer.objects.get(session_id=session_id)

    parsed_url = urlparse(request.META['HTTP_REFERER'])
    parsed_query = parsed_url.query
    modal_id = ''
    if parsed_query:
        query_params = parsed_query.split('&')
        for param in query_params:
            if param.split('=')[0] == 'modal_id':
                modal_id = param.split('=')[1]
                break

    if not obj:
        last_order = customer.order_set.last()
        if last_order:
            obj = last_order.goods or last_order.service

    if obj and modal_id != 'callback-modal':
        obj_class = type(obj)
        obj_name = 'товар' if obj_class == Goods else 'услуга'
        link = f'https://{settings.ALLOWED_HOSTS[0]}{reverse("goods") + "?modal=detail-view-modal-" + str(obj.pk)}' if obj_class == Goods else ''
        availability = f'Наличие на сайте: {obj.count} ' if obj_class == Goods else ''
        customer_message = request.POST.get('text')

        message = dedent(f"""
            Запрос клиента 
            {str(customer) + ", Телефон - " + customer.phone_number if customer.phone_number 
                else str(customer) + " нажал кнопку заказать " + obj_name + ", но еще не предоставил свои контактные данные, проверьте наличие и другие характеристики."}
            Заказ: {obj_name} - {obj.title}
            {availability}
            Стоимость на сайте: {'от' if obj.price_prefix else ''} {obj.price}
            {link}
            {'Сообщение от пользователя: ' + customer_message if customer_message else ''}
            """)

    elif obj:
        obj_class = type(obj)
        obj_name = 'товар' if obj_class == Goods else 'услуга'
        link = f'https://{settings.ALLOWED_HOSTS[0]}{reverse("goods") + "?modal=detail-view-modal-" + str(obj.pk)}' if obj_class == Goods else ''
        availability = f'Наличие на сайте: {obj.count} ' if obj_class == Goods else ''
        customer_message = request.POST.get('text')
        message = dedent(f"""
            Запрос клиента 
            {customer}, Телефон - {customer.phone_number}
            {'Сообщение от пользователя: ' + customer_message if customer_message else ''}
            Пользователь заказал обратный звонок на сайте.
            Последний заказ пользователя: {obj_name} - {obj.title}
            {availability}
            Стоимость на сайте: {'от' if obj.price_prefix else ''} {obj.price}
            {link}
            """)

    elif customer.phone_number:
        customer_message = request.POST.get('text')
        message = dedent(f"""
            Запрос клиента 
            {customer}, Телефон - {customer.phone_number}
            {'Сообщение от пользователя: ' + customer_message if customer_message else ''}
            Пользователь заказал обратный звонок на сайте. Заказанные услуги отсутствуют.
            """)
    else:
        message = "Ошибка при формировании сообщения"

    return message


def send_telegram_message(message_text):
    bot_token = os.environ['TELEGRAM_ADMIN_BOT_TOKEN']
    chat_id = TELEGRAM_ADMIN_CHAT_ID
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message_text}'
    response = requests.get(send_text)

    return response.json()
