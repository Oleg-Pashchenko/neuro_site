import uuid

from yookassa import Configuration, Payment


def yookassa_payment():
    Configuration.account_id = '233288'
    Configuration.secret_key = 'live_cxhdaLZwHpRVvHlFPpNYKSbqxpt9VO_Unok-suc-AqQ'

    payment = Payment.create({
        "amount": {
            "value": "100.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "capture": True,
        "description": "Заказ №1"
    }, uuid.uuid4())

    # payment = Payment.find_one(payment_id)

def stripe():
    pass


def cryptomus():
    pass
