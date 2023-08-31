from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from neuro_site.amo_auth import update_pipelines, get_text_by_pipeline, set_text_by_pipeline, get_pipelines
from neuro_site.db_conn import get_token


def change_lang(request):
    if request.method == 'POST':
        print(request.POST.dict())
        return render(request, 'index.html')


def index(request):
    return render(request, 'index.html')


def get_text(request):
    pipeline = request.GET.dict()['pipeline']
    pipeline = int(pipeline.split('(')[1].split(',')[0])
    print(pipeline, 'PIPELINE')
    info = get_text_by_pipeline(pipeline)
    print(info)
    text, model, fmodel, tokens, temperature, voice = info[1], info[2], info[3], info[4], info[5], info[6]
    return JsonResponse({
        'text': text,
        'model': model,
        'fmodel': fmodel,
        'tokens': tokens,
        'temperature': temperature,
        'voice': 'active' if voice == 1 else 'passive'
    })


def set_text(request):
    print(request.GET.dict())
    tokens = request.GET.dict()['tokens']
    temperature = request.GET.dict()['temperature']
    vm = request.GET.dict()['vm']
    model = request.GET.dict()['model']
    ftmodel = request.GET.dict()['ftmodel']
    pipeline = request.GET.dict()['pipeline']
    pipeline = int(pipeline.split('(')[1].split(',')[0])
    text = request.GET.dict()['text']
    print(text, 'это текст')
    set_text_by_pipeline(pipeline, text, tokens, temperature, vm, model, ftmodel)
    return JsonResponse({'status': 'ok'})

def faq(request):
    return render(request, "faq.html")


@login_required()
def home(request):
    return render(request, "main.html")


@login_required()
def admin(request):
    return render(request, 'admin.html')


@login_required()
def payment(request):
    return render(request, 'payment.html')


#@login_required()
def settings(request):
    update_pipelines()
    api_token = get_token()
    pipelines = get_pipelines()
    return render(request, 'settings.html', {
        'pipelines': pipelines,
        'api_token': api_token
    })


def save_token(request):
    pass


@login_required()
def stats(request):
    return render(request, 'stats.html')
