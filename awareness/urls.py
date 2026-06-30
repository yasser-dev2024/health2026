from django.urls import path

from . import views

app_name = 'awareness'

urlpatterns = [
    path('downloads/', views.downloads_view, name='downloads'),
    path('messages/', views.messages_view, name='messages'),
]
