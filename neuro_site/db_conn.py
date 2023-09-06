import os

import psycopg2


def get_token(owner_name):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM request_settings WHERE owner_name=%s;", (owner_name,))
    token = cur.fetchone()[0]
    conn.close()
    return token


def set_token(api_key):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("UPDATE request_settings SET api_key=%s", (api_key,))
    conn.commit()
    conn.close()
