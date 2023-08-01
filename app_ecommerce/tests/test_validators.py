import pytest
from django.core.exceptions import ValidationError

from app_ecommerce.tests.data import TEST_PHONE_NUMBERS
from app_ecommerce.validators import phone_number_validator


class TestPhoneNumberValidator:
    @staticmethod
    @pytest.mark.parametrize("value", TEST_PHONE_NUMBERS['valid'])
    def test_valid_phone_numbers(value):
        phone_number_validator(value)

    @staticmethod
    @pytest.mark.parametrize("value", TEST_PHONE_NUMBERS['invalid'])
    def test_invalid_phone_numbers(value):
        with pytest.raises(ValidationError):
            phone_number_validator(value)
