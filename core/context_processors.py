from campaigns.services import get_active_campaign

from .models import GeneralSettings


def site_settings(request):
    campaign = get_active_campaign()
    settings = None
    if campaign:
        settings = GeneralSettings.objects.filter(campaign=campaign).order_by('-updated_at').first()
    settings = settings or GeneralSettings.objects.order_by('-updated_at').first()
    return {
        'active_campaign': campaign,
        'site_settings': settings,
    }
