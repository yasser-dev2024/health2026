from django.urls import path

from . import views

app_name = 'qr'

urlpatterns = [
    path('<slug:slug>/', views.qr_location_view, name='location'),
    path('item/<int:item_id>/', views.qr_item_view, name='item'),
]
