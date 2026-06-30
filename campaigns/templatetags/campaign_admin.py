from django import template

from campaigns.models import Campaign
from campaigns.services import campaign_stats, get_active_campaign
from qr.models import QrLocation


register = template.Library()


@register.simple_tag
def campaign_admin_summary():
    active_campaign = get_active_campaign()
    qr_locations = QrLocation.objects.all()
    if active_campaign and any(field.name == 'campaign' for field in QrLocation._meta.fields):
        qr_locations = qr_locations.filter(campaign=active_campaign)
    return {
        'active_campaign': active_campaign,
        'active_stats': campaign_stats(active_campaign) if active_campaign else campaign_stats(),
        'all_stats': campaign_stats(),
        'campaign_count': Campaign.objects.count(),
        'archived_count': Campaign.objects.filter(status=Campaign.STATUS_ARCHIVED).count(),
        'qr_locations_count': qr_locations.count(),
    }
