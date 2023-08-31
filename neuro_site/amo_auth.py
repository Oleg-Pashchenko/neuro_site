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
    return token, session


def update_pipelines():
    token, session = get_token()
    response = session.get('https://appgpt.amocrm.ru/leads/pipeline/').text
    response = response.split('"pipeline_id":')[1::]
    pipelines = set()
    for r in response:
        try:
            pipelines.add(int(r.split(',')[0]))
        except:
            pass
    pipelines_from_db = get_db_pipelines()
    to_delete = []
    to_add = []
    for p in pipelines:
        if p not in pipelines_from_db:
            to_add.append(p)
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
    cur.execute("SELECT pipeline_id FROM pipelines;")
    text = cur.fetchall()
    conn.close()
    return text



def get_db_pipelines():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute('SELECT * FROM pipelines;', )
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
    for id in ids:
        cur.execute('INSERT INTO pipelines (pipeline_id, text) VALUES (%s, %s);', (id, ''))
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
    cur.execute("SELECT * FROM pipelines WHERE pipeline_id=%s", (pipeline,))
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
    cur.execute("UPDATE pipelines SET text=%s, model=%s, ftmodel=%s, tokens=%s, temperature=%s, voice=%s WHERE pipeline_id=%s;",
                (text, model, ftmodel, int(tokens), int(temperature), int(vm=='active'), pipeline))
    conn.commit()
    conn.close()
