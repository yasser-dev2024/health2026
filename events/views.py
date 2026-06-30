from django.shortcuts import render

from campaigns.services import campaign_queryset, get_active_campaign

from .models import HealthEvent


def events_view(request):
    campaign = get_active_campaign()
    events = campaign_queryset(HealthEvent.objects.filter(active=True), campaign=campaign).order_by('order', 'date', 'time')
    return render(request, 'events/list.html', {'events': events})

# Create your views here.
