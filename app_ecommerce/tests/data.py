TEST_DATA = {
     'customer_name': 'Leonid',
     'customer_phone_number': '+79277777777',
     'customer_message': 'Test message from customer',
     'top_level_category_title': 'Top category',
     'second_level_category_title': 'Second category',
     'session_key': 'test_session_key',
}

TEST_PHONE_NUMBERS = {
    'valid': ['+79277535560', '+7(927)753-55-60', '+7 927 753 55 60',
              '+7 927 753 55-60', '+7 927 753 5560', '89277535560', '8(927) 753 55-60'],
    'invalid': ['invalidnumber', '2344234234', 'invalid3423', '+7invalid',
                '927 753 55 60', '927-753-55-60']
}