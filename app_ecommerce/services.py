import os
from textwrap import dedent

import requests
from django.http import Http404
from django.urls import reverse

from app_ecommerce.models import Goods, Customer
from carkeys_project.settings import TELEGRAM_ADMIN_CHAT_ID


def construct_message(request, goods=None):
    session_id = request.session.session_key
    customer = Customer.objects.get(session_id=session_id)

    if not goods:
        last_order = customer.order_set.last()
        if last_order:
            goods = last_order.goods

    if goods and not customer.phone_number:
        message = dedent(f"""
            Запрос клиента 
            Заказана услуга: {goods.title}
            Наличие на сайте: {goods.count} 
            Стоимость на сайте: {goods.price}
            Пользователь {customer.name} нажал кнопку заказать услугу, но еще не предоставил свои контактные данные, \
            проверьте наличие указанного товара, его фактическое наличие и другие характеристики.
            Ссылка: {reverse('goods') + '?modal=detail-view-modal-' + str(goods.pk)}
            """)
    elif goods and customer.phone_number:
        message = dedent(f"""
            Запрос клиента 
            Пользователь: Имя - {customer.name}, Телефон - {customer.phone_number}
            Заказана услуга: {goods.title}
            Наличие на сайте: {goods.count} 
            Стоимость на сайте: {goods.price}
            Ссылка: {reverse('goods') + '?modal=detail-view-modal-' + str(goods.pk)}
            """)
    elif customer.phone_number:
        message = dedent(f"""
            Запрос клиента 
            Пользователь: Имя - {customer.name}, Телефон - {customer.phone_number}
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
