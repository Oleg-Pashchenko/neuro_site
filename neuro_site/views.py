from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def change_lang(request):
    if request.method == 'POST':
        print(request.POST.dict())
        return render(request, 'index.html')

def index(request):
    return render(request, 'index.html')


def faq(request):
    return render(request, "faq.html")


@login_required()
def main(request):
    return render(request, "main.html")


@login_required()
def admin(request):
    return render(request, 'admin.html')


@login_required()
def payment(request):
    return render(request, 'payment.html')


@login_required()
def settings(request):
    return render(request, 'settings.html')


@login_required()
def stats(request):
    return render(request, 'stats.html')
