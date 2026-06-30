from django.shortcuts import get_object_or_404, render

from .models import CampaignPage
from .services import get_active_campaign, record_campaign_interaction


def campaign_page_view(request, page_key):
    campaign = get_active_campaign()
    page = get_object_or_404(CampaignPage, campaign=campaign, key=page_key, active=True)
    record_campaign_interaction(request, 'visit', campaign=campaign, page=page.key)
    return render(request, 'campaigns/page.html', {'campaign': campaign, 'campaign_page': page})
