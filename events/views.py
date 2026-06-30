from django.shortcuts import render

from .models import HealthEvent


def events_view(request):
    events = HealthEvent.objects.filter(active=True).order_by('order', 'date', 'time')
    return render(request, 'events/list.html', {'events': events})

# Create your views here.
