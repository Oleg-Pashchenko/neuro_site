import os

import psycopg2
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from neuro_site import db_conn, amo_auth
from neuro_site.amo_auth import update_pipelines, get_text_by_pipeline, set_text_by_pipeline, get_pipelines


def change_lang(request):
    if request.method == 'POST':
        print(request.POST.dict())
        return render(request, 'index.html')


def index(request):
    return render(request, 'index.html')


@login_required()
def get_text(request):
    pipeline = request.GET.dict()['pipeline']
    print(pipeline)
    info = get_text_by_pipeline(pipeline)
    text, model, fmodel, tokens, temperature, voice = info[1], info[2], info[3], info[4], info[5], info[6]
    return JsonResponse({
        'openai': db_conn.get_token(str(request.user)),
        'text': text,
        'model': model,
        'fmodel': fmodel,
        'tokens': tokens,
        'temperature': temperature,
        'voice': 'active' if voice == 1 else 'passive'
    })

@login_required()
def update_pipelines(request):
    user = str(request.user)
    token, session, headers = amo_auth.get_token(user)
    response = session.get('https://appgpt.amocrm.ru/ajax/v1/pipelines/list', headers=headers).json()['response'][
        'pipelines']
    pipelines = set()

    for r in response.keys():
        pipelines.add(int(r))

    pipelines_from_db = amo_auth.get_db_pipelines_id(user)
    to_delete = []
    to_add = []
    for p in pipelines:
        if p not in pipelines_from_db:
            to_add.append([p, response[str(p)]['name'], response[str(p)]['sort']])
    for p in pipelines_from_db:
        if p not in pipelines:
            to_delete.append(p)
    amo_auth.add_pipelines(to_add, user)
    amo_auth.delete_pipelines(to_delete)
    return pipelines


def set_text(request):
    print(request.GET.dict())
    tokens = request.GET.dict()['tokens']
    temperature = request.GET.dict()['temperature']
    vm = request.GET.dict()['vm']
    model = request.GET.dict()['model']
    ftmodel = request.GET.dict()['ftmodel']
    pipeline = request.GET.dict()['pipeline']
    openai_token = request.GET.dict()['openai-token']
    db_conn.set_token(openai_token)
    text = request.GET.dict()['text']
    print(text, 'это текст')
    set_text_by_pipeline(pipeline, text, tokens, temperature, vm, model, ftmodel)
    return JsonResponse({'status': 'ok'})


def faq(request):
    return render(request, "faq.html")


@login_required()
def manual_amo_create(request):
    user = str(request.user)
    form = request.POST.dict()
    h, m, p, a_id = form['host'], form['email'], form['password'], form['account_chat_id']
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    print(h, m, p, a_id, user)
    cur.execute(
        "UPDATE request_settings SET amo_host=%s, amo_login=%s, amo_password=%s, amo_chat_id=%s WHERE owner_name=%s;",
        (h, m, p, a_id, user,))
    conn.commit()
    conn.close()
    return redirect('settings')


@login_required()
def home(request):
    print(request.user)
    return render(request, "main.html")


@login_required()
def manually_register(request):
    return render(request, 'manually_register.html', {
        'username': str(request.user)
    })


@login_required()
def admin(request):
    return render(request, 'admin.html')


@login_required()
def payment(request):
    return render(request, 'payment.html')


@login_required()
def settings(request):
    pipelines = get_pipelines(str(request.user))
    return render(request, 'settings.html', {
        'pipelines': pipelines,
        'username': str(request.user)
    })


@login_required()
def stats(request):
    return render(request, 'stats.html')
