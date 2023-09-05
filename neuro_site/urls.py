"""
URL configuration for neuro_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name=''),
    path('api/v1/change-lang', views.change_lang, name='change_lang'),
    path('api/v1/settings/get-text', views.get_text, name='get_text'),
    path('api/v1/settings/set-text', views.set_text, name='set_text'),
    path('faq/', views.faq, name='faq'),
    path('home/', views.home, name='home'),
    path('manually-register/', views.manually_register, name='manually_register'),
    path('admin/', views.admin, name='admin'),
    path('payment/', views.payment, name='payment'),
    path('settings/', views.settings, name='settings'),
    path('stats/', views.stats, name='stats'),
    path('manual_amo_create/', views.manual_amo_create, name='manual_amo_create'),
    path('', include('session_auth_app.urls'))
]
