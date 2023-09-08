import datetime
import os
import random
import uuid

import psycopg2
from yookassa import Configuration, Payment
import dotenv

dotenv.load_dotenv()
Configuration.account_id = '233288'
Configuration.secret_key = 'live_cxhdaLZwHpRVvHlFPpNYKSbqxpt9VO_Unok-suc-AqQ'


def yookassa_payment(money, user, sub_type):
    payment = Payment.create({
        "amount": {
            "value": money,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"http://127.0.0.1:8000/payment/"
        },
        "capture": True,
        "description": f"Оплата подписки пользователя {user}."
    }, uuid.uuid4())

    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()

    print(payment.id)
    cur.execute(
        "INSERT INTO payments (owner_name, money, subscription_type, payment_id, is_suggested, date, method) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (user, money, sub_type, payment.id, False, datetime.datetime.now().date(), 'YooKassa',))
    conn.commit()
    conn.close()
    return payment.confirmation.confirmation_url
    #


def get_days_by_type(element):
    if element == 1:
        days = 30
    elif element == 2:
        days = 90
    elif element == 3:
        days = 180
    else:
        days = 365
    return days


def check_subs_status(user):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM payments WHERE owner_name=%s AND is_suggested=%s", (user, False,))
    elements = cur.fetchall()
    for element in elements:
        payment = Payment.find_one(element[3])
        if payment.status == 'succeeded':
            cur.execute('UPDATE payments SET is_suggested=%s WHERE payment_id=%s', (True, payment.id,))

            days = get_days_by_type(element[2])
            cur.execute('INSERT INTO subscriptions (owner_name, subscription_type, days_count) VALUES (%s, %s, %s)',
                        (user, element[2], days,))
            conn.commit()
    # TODO: Сделать уменьшение количества дней подписки каждый день
    conn.close()


def get_transactions_history(user):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM payments WHERE owner_name=%s AND is_suggested=%s", (user, True,))
    elements = cur.fetchall()
    conn.close()
    result = []
    for element in elements:
        result.append(
            {'date': element[5], 'method': element[6], 'summ': element[1], 'range': get_days_by_type(element[2])})
    return result


def get_subscription_info(user):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM subscriptions WHERE owner_name=%s", (user,))
    elements = cur.fetchall()
    conn.close()
    days = 0
    for element in elements:
        days += element[2]
    return {'days': days}


def get_payment_data(user):
    check_subs_status(user)
    transactions = get_transactions_history(user)
    sub_info = get_subscription_info(user)
    return {
        'transactions': transactions,
        'subscribtion': sub_info
    }


def stripe():
    pass


def cryptomus():
    pass
