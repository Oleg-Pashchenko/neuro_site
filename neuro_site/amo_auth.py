import os
import time
import requests
import psycopg2
import dotenv

dotenv.load_dotenv()


def get_token():
    mail = 'odpash.itmo@gmail.com'
    host = 'https://appgpt.amocrm.ru/'
    host2 = 'appgpt.amocrm.ru'
    password = "developer2023"
    try:
        session = requests.Session()
        response = session.get(host)
        session_id = response.cookies.get('session_id')
        csrf_token = response.cookies.get('csrf_token')
        headers = {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': f'session_id={session_id}; '
                      f'csrf_token={csrf_token};'
                      f'last_login={mail}',
            'Host': host.replace('https://', '').replace('/', ''),
            'Origin': host,
            'Referer': host,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36'
        }
        payload = {
            'csrf_token': csrf_token,
            'password': password,
            'temporary_auth': "N",
            'username': mail}

        response = session.post(f'{host}oauth2/authorize', headers=headers, data=payload)
        access_token = response.cookies.get('access_token')
        refresh_token = response.cookies.get('refresh_token')
        print(access_token)
        print(refresh_token)
        headers['access_token'], headers['refresh_token'] = access_token, refresh_token
        payload = {'request[chats][session][action]': 'create'}
        headers['Host'] = host2
        response = session.post(f'{host}ajax/v1/chats/session', headers=headers, data=payload)
        token = response.json()['response']['chats']['session']['access_token']
    except Exception as e:
        print(e)
        time.sleep(3)
        return get_token()
    print('Amo Token:', token)
    return token, session, headers


def update_pipelines():
    token, session, headers = get_token()
    response = session.get('https://appgpt.amocrm.ru/ajax/v1/pipelines/list', headers=headers).json()['response'][
        'pipelines']
    pipelines = set()

    for r in response.keys():
        pipelines.add(int(r))

    pipelines_from_db = get_db_pipelines_id()
    to_delete = []
    to_add = []
    for p in pipelines:
        if p not in pipelines_from_db:
            to_add.append([p, response[str(p)]['name'], response[str(p)]['sort']])
    for p in pipelines_from_db:
        if p not in pipelines:
            to_delete.append(p)
    add_pipelines(to_add)
    delete_pipelines(to_delete)
    return pipelines

def get_pipelines():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT name FROM pipelines ORDER BY number;")
    resp = []

    text = cur.fetchall()
    for i in text:
        resp.append(i[0])
    conn.close()
    return resp


def get_db_pipelines_id():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute('SELECT pipeline_id FROM pipelines;', )
    records = cur.fetchall()
    resp = []
    for r in records:
        resp.append(r[0])
    conn.close()
    return resp


def add_pipelines(ids):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    for el in ids:
        cur.execute('INSERT INTO pipelines (pipeline_id, name, text, number) VALUES (%s, %s, %s, %s);', (el[0], el[1], '', el[2]))
        conn.commit()
    conn.close()


def delete_pipelines(ids):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    for id in ids:
        cur.execute('DELETE FROM pipelines WHERE pipeline_id=%s;', (id,))
        conn.commit()
    conn.close()


def get_text_by_pipeline(pipeline):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM pipelines WHERE name=%s", (pipeline,))
    text = cur.fetchone()
    conn.close()
    return text


def set_text_by_pipeline(pipeline, text, tokens, temperature, vm, model, ftmodel):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    if tokens == '':
        tokens = 0

    if temperature == '':
        temperature = 1

    cur.execute(
        "UPDATE pipelines SET text=%s, model=%s, ftmodel=%s, tokens=%s, temperature=%s, voice=%s WHERE name=%s;",
        (text, model, ftmodel, int(tokens), int(temperature), int(vm == 'active'), pipeline.strip(),))
    conn.commit()
    conn.close()
