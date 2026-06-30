from django.shortcuts import render

from awareness.models import AwarenessMessage
from campaigns.models import CampaignInteraction
from campaigns.services import campaign_queryset, get_active_campaign, record_campaign_interaction
from events.models import HealthEvent
from journey.forms import JourneyForm
from qr.services import record_home_qr_scan

from .services import get_home_context


def home_view(request):
    campaign = get_active_campaign()
    context = get_home_context()
    qr_slug = request.GET.get('qr', '').strip().lower()
    qr_result = None
    if qr_slug:
        qr_result = record_home_qr_scan(request, qr_slug)
    else:
        record_campaign_interaction(request, CampaignInteraction.TYPE_VISIT, campaign=campaign)

    featured_events = campaign_queryset(
        HealthEvent.objects.filter(active=True, show_on_home=True),
        campaign=campaign,
    ).order_by('order', 'date')[:3]
    messages = campaign_queryset(
        AwarenessMessage.objects.filter(active=True),
        campaign=campaign,
    ).order_by('order', 'id')[:4]

    context.update(
        {
            'featured_events': featured_events,
            'messages': messages,
            'journey_form': JourneyForm(),
            'qr_welcome_location': qr_result['location'] if qr_result else None,
            'qr_welcome_name': request.GET.get('qrName', ''),
        }
    )
    return render(request, 'home.html', context)

# Create your views here.
