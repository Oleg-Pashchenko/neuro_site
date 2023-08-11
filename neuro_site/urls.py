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
    path('faq/', views.faq, name='faq'),
    path('main/', views.main, name='main'),
    path('admin/', views.admin, name='admin'),
    path('payment/', views.payment, name='payment'),
    path('settings/', views.settings, name='settings'),
    path('stats/', views.stats, name='stats'),
    path('', include('session_auth_app.urls'))
]
