import os

import psycopg2
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm


def create_settings(username):
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO request_settings (owner_name) VALUES (%s)", (username,))
    conn.commit()
    conn.close()


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            create_settings(form.cleaned_data['username'])
            return redirect('login')  # Перенаправьте пользователя на страницу входа после успешной регистрации
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')  # Перенаправьте пользователя на главную страницу после успешного входа
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})
