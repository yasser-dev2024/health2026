from django.shortcuts import render

from .models import HealthLocation


def nearby_view(request):
    selected_type = request.GET.get('type', '')
    locations = HealthLocation.objects.filter(active=True).order_by('order', 'city', 'name')
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
