from django.urls import path

from . import views

app_name = 'passport'

urlpatterns = [
    path('', views.passport_view, name='passport'),
]
