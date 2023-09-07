import os
import time
import requests
import psycopg2
import dotenv

dotenv.load_dotenv()


def get_token(owner):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM request_settings WHERE owner_name=%s;", (owner,))
    info = cur.fetchone()
    conn.close()
    mail = info[3]
    host = info[2]
    host2 = host.replace('https://', '').replace('/', '')
    password = info[4]
    # mail = 'odpash.itmo@gmail.com'
    # host = 'https://appgpt.amocrm.ru/'
    # host2 = 'appgpt.amocrm.ru'
    # password = "developer2023"
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
        return get_token(owner)
    print('Amo Token:', token)
    return token, session, headers





def get_pipelines(user):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("SELECT name FROM pipelines WHERE owner_name = %s ORDER BY number;", (user,))
    resp = []
    text = cur.fetchall()
    for i in text:
        resp.append(i[0])
    conn.close()
    return resp


def get_db_pipelines_id(user):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute('SELECT pipeline_id FROM pipelines WHERE owner_name=%s;', (user,))
    records = cur.fetchall()
    resp = []
    for r in records:
        resp.append(r[0])
    conn.close()
    return resp


def add_pipelines(ids, user):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    for el in ids:
        cur.execute('INSERT INTO pipelines (pipeline_id, name, text, number, owner_name) VALUES (%s, %s, %s, %s, %s);',
                    (el[0], el[1], '', el[2], user,))
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


def get_chats_count_by_pipeline(pipeline_id, host, mail, password):
    url = f'https://chatgpt.amocrm.ru/ajax/leads/sum/{pipeline_id}/'
    token, session, headers = get_token('tester')
    resp = session.get(f'https://appgpt.amocrm.ru/leads/pipeline/{pipeline_id}/?skip_filter=Y')
    items = resp.text.split('"leads_info_by_status":[')[1].split('{"ID":')[1::]
    data = {'leads_by_status': 'Y', 'skip_filter': 'Y', f'filter[pipe][{pipeline_id}][]': []}
    for i in items:
        i = i.split(',')[0]
        if i.isdigit():
            data[f'filter[pipe][{pipeline_id}][]'].append(int(i.split(',')[0].strip()))
    response = session.post(url, headers=headers, data=data).json()
    return response['all_count']


#get_chats_count_by_pipeline(7173574, 'https://appgpt.amocrm.ru/', 'odpash.itmo@gmail.com', 'developer2023')
