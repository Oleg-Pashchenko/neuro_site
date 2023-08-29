from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from neuro_site.amo_auth import update_pipelines, get_text_by_pipeline, set_text_by_pipeline, get_pipelines


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
    text = get_text_by_pipeline(pipeline)[0]
    print(text)
    return JsonResponse({'text': text})


def set_text(request):
    pipeline = request.GET.dict()['pipeline']
    pipeline = int(pipeline.split('(')[1].split(',')[0])
    text = request.GET.dict()['text']
    print(text, 'это текст')
    set_text_by_pipeline(pipeline, text)
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
    pipelines = get_pipelines()
    return render(request, 'settings.html', {'pipelines': pipelines})


@login_required()
def stats(request):
    return render(request, 'stats.html')
