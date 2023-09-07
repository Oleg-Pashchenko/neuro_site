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


def pipeline_id_by_name_and_user(pipeline, user):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT pipeline_id FROM pipelines WHERE name=%s AND owner_name=%s", (pipeline, user,))
    element = cur.fetchone()
    conn.close()
    return element[0]


def get_get_stats_by_pipeline_id(pipeline_id):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM stats WHERE pipeline_id=%s", (pipeline_id,))
    elements = cur.fetchall()
    conn.close()

    chats_count = []
    openai_cost = []
    values, dates = [], []
    for el in elements:
        dates.append(el[4])
        values.append(el[1])
    messages_count = {'values': values, 'dates': dates}

    values, dates = [], []
    for el in elements:
        dates.append(el[4])
        values.append(el[2])
    chats_count = {'values': values, 'dates': dates}

    values, dates = [], []
    for el in elements:
        dates.append(el[4])
        values.append(el[3])
    openai_cost = {'values': values, 'dates': dates}
    return {
        'messages_count': messages_count,
        'chats_count': chats_count,
        'openai_cost': openai_cost
    }


def get_stats_db(pipelines, user):
    pipeline_ids = []
    for pipeline in pipelines:
        pipeline_id = pipeline_id_by_name_and_user(pipeline, user)
        stats = get_get_stats_by_pipeline_id(pipeline_id)
        pipeline_ids.append({
            'id': pipeline_id,
            'name': pipeline,
            'messages_count': stats['messages_count'],
            'chats_count': stats['chats_count'],
            'openai_cost': stats['openai_cost']
        }
        )
    return pipeline_ids
