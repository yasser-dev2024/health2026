from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from campaigns.services import get_active_campaign
from core.utils import get_visitor_id
from .models import QrLocation, QrVisitorProfile
from .services import record_item_scan, record_location_scan


def qr_location_view(request, slug):
    result = record_location_scan(request, slug)
    if result['location'].target_url:
        return redirect(result['location'].target_url)
    return render(request, 'qr/scan_result.html', {'result': result, 'scan_type': 'location'})


def qr_item_view(request, item_id):
    result = record_item_scan(request, item_id)
    return render(request, 'qr/scan_result.html', {'result': result, 'scan_type': 'item'})


@require_POST
def qr_profile_view(request):
    campaign = get_active_campaign()
    visitor_id = get_visitor_id(request)
    profile, _ = QrVisitorProfile.objects.get_or_create(campaign=campaign, visitor_id=visitor_id)

    location_id = request.session.get('qr_start_location_id')
    if location_id:
        profile.qr_location = QrLocation.objects.filter(pk=location_id).first()

    allowed_fields = {
        'visitor_type': {value for value, _ in QrVisitorProfile.VISITOR_TYPE_CHOICES},
        'party_type': {value for value, _ in QrVisitorProfile.PARTY_TYPE_CHOICES},
        'age_group': {value for value, _ in QrVisitorProfile.AGE_GROUP_CHOICES},
        'health_topic': {value for value, _ in QrVisitorProfile.HEALTH_TOPIC_CHOICES},
    }

    for field_name, allowed_values in allowed_fields.items():
        value = request.POST.get(field_name, '').strip()
        if value in allowed_values:
            setattr(profile, field_name, value)

    profile.save()
    return JsonResponse({'ok': True})

# Create your views here.
