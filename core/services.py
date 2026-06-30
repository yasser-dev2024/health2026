from django.db.models import Q

from campaigns.models import CampaignButton
from campaigns.services import get_active_campaign, get_campaign_home_page

from .models import FeatureFlag, GeneralSettings, HomeConfig, HomeQuickButton, SmartEntryConfig


def get_home_context():
    campaign = get_active_campaign()
    home_qs = HomeConfig.objects.filter(active=True)
    quick_button_qs = HomeQuickButton.objects.filter(active=True)
    settings_qs = GeneralSettings.objects.all()
    smart_entry_qs = SmartEntryConfig.objects.filter(active=True)
    feature_flag_qs = FeatureFlag.objects.all()

    if campaign:
        home = home_qs.filter(campaign=campaign).order_by('-updated_at').first() or home_qs.order_by('-updated_at').first()
        legacy_buttons = quick_button_qs.filter(campaign=campaign).order_by('order', 'id')
        settings = settings_qs.filter(campaign=campaign).order_by('-updated_at').first() or settings_qs.order_by('-updated_at').first()
        smart_entry = smart_entry_qs.filter(campaign=campaign).order_by('-updated_at').first() or smart_entry_qs.order_by('-updated_at').first()
        feature_flag_qs = feature_flag_qs.filter(Q(campaign=campaign) | Q(campaign__isnull=True))
    else:
        home = home_qs.order_by('-updated_at').first()
        legacy_buttons = quick_button_qs.order_by('order', 'id')
        settings = settings_qs.order_by('-updated_at').first()
        smart_entry = smart_entry_qs.order_by('-updated_at').first()

    campaign_home_page = get_campaign_home_page(campaign)
    dynamic_buttons = CampaignButton.objects.none()
    if campaign and campaign_home_page:
        dynamic_buttons = CampaignButton.objects.filter(
            Q(page=campaign_home_page) | Q(page__isnull=True),
            campaign=campaign,
            active=True,
        ).order_by('order', 'id')
    quick_buttons = dynamic_buttons if dynamic_buttons.exists() else legacy_buttons
    feature_flags = {
        flag.key: flag.enabled for flag in feature_flag_qs
    }

    return {
        'active_campaign': campaign,
        'campaign_home_page': campaign_home_page,
        'home_config': home,
        'quick_buttons': quick_buttons,
        'general_settings': settings,
        'smart_entry': smart_entry,
        'feature_flags': feature_flags,
    }
