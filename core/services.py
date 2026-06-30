from .models import FeatureFlag, GeneralSettings, HomeConfig, HomeQuickButton, SmartEntryConfig


def get_home_context():
    home = HomeConfig.objects.filter(active=True).order_by('-updated_at').first()
    quick_buttons = HomeQuickButton.objects.filter(active=True).order_by('order', 'id')
    settings = GeneralSettings.objects.order_by('-updated_at').first()
    smart_entry = SmartEntryConfig.objects.filter(active=True).order_by('-updated_at').first()
    feature_flags = {
        flag.key: flag.enabled for flag in FeatureFlag.objects.all()
    }

    return {
        'home_config': home,
        'quick_buttons': quick_buttons,
        'general_settings': settings,
        'smart_entry': smart_entry,
        'feature_flags': feature_flags,
    }
