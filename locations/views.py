from django.shortcuts import render

from campaigns.services import campaign_queryset, get_active_campaign

from .models import HealthLocation


def nearby_view(request):
    campaign = get_active_campaign()
    selected_type = request.GET.get('type', '')
    locations = campaign_queryset(HealthLocation.objects.filter(active=True), campaign=campaign).order_by('order', 'city', 'name')
    if selected_type:
        locations = locations.filter(location_type=selected_type)

    return render(
        request,
        'locations/nearby.html',
        {
            'locations': locations,
            'selected_type': selected_type,
            'location_types': HealthLocation.TYPE_CHOICES,
        },
    )

# Create your views here.
