from django.shortcuts import render

from awareness.models import AwarenessMessage
from events.models import HealthEvent
from journey.forms import JourneyForm
from qr.services import record_home_qr_scan

from .services import get_home_context


def home_view(request):
    context = get_home_context()
    qr_slug = request.GET.get('qr', '').strip().lower()
    qr_result = None
    if qr_slug:
        qr_result = record_home_qr_scan(request, qr_slug)

    context.update(
        {
            'featured_events': HealthEvent.objects.filter(active=True, show_on_home=True).order_by('order', 'date')[:3],
            'messages': AwarenessMessage.objects.filter(active=True).order_by('order', 'id')[:4],
            'journey_form': JourneyForm(),
            'qr_welcome_location': qr_result['location'] if qr_result else None,
            'qr_welcome_name': request.GET.get('qrName', ''),
        }
    )
    return render(request, 'home.html', context)

# Create your views here.
