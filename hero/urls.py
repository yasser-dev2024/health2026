from django.urls import path

from . import views

app_name = 'hero'

urlpatterns = [
    path('', views.hero_view, name='hero'),
]
