import phonenumbers
from django.core.exceptions import ValidationError
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type, NumberParseException
from django.utils.translation import gettext_lazy as _


def phone_number_validator(value):
    message = _('Incorrect phone number')
    code = 'Phone number validation error'
    number = value
    try:
        carrier._is_mobile(number_type(phonenumbers.parse(number)))
    except NumberParseException:
        raise ValidationError(message, code=code)