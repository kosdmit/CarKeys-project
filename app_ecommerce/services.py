import os

import requests
from telegram import Bot

from app_ecommerce.models import MODELS
from carkeys_project.settings import TELEGRAM_ADMIN_CHAT_ID


def construct_message(data):
    obj_id = data.get('obj_id')
    obj_type = data.get('obj_type')
    obj = MODELS[obj_type].objects.get(pk=obj_id)
    message_type = data.get('message_type')

    message = f"""
Системное уведомление
Заказана услуга: {obj.title}
Наличие на сайте: {obj.count} 
Стоимость на сайте: {obj.price}
Пользователь нажал кнопку заказать услугу, но еще не предоставил свои контактные данные, \
проверьте наличие указанного товара, его фактическое наличие и другие характеристики.
Ссылка:
"""

    return message


def send_telegram_message(message_text):
    bot_token = os.environ['TELEGRAM_ADMIN_BOT_TOKEN']
    chat_id = TELEGRAM_ADMIN_CHAT_ID
    send_text = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message_text}'
    response = requests.get(send_text)

    return response.json()
