from .models import GeneralSettings


def site_settings(request):
    settings = GeneralSettings.objects.order_by('-updated_at').first()
    return {
        'site_settings': settings,
    }
