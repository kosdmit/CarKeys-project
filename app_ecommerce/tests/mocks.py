def mock_send_telegram_message(message):
    return {"status": "success"}

def mock_construct_message(request, obj=None):
    return "Some message"