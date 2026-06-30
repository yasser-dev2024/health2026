from django.db import migrations


DEFAULT_SLUG = 'summer-health'


def seed_summer_health_campaign(apps, schema_editor):
    Campaign = apps.get_model('campaigns', 'Campaign')
    CampaignPage = apps.get_model('campaigns', 'CampaignPage')
    CampaignButton = apps.get_model('campaigns', 'CampaignButton')

    HomeConfig = apps.get_model('core', 'HomeConfig')
    HomeQuickButton = apps.get_model('core', 'HomeQuickButton')

    home = HomeConfig.objects.order_by('-updated_at').first()
    title = getattr(home, 'platform_name', '') or 'صيف وصحة - مساعد'
    tagline = getattr(home, 'tagline', '') or 'مرشدك الصحي في صيف عسير'
    intro = getattr(home, 'intro', '') or 'منصة صحية وتوعوية لزوار منطقة عسير.'
    hero_image = getattr(home, 'hero_image', '') or 'img/asir-hero.png'

    campaign, created = Campaign.objects.get_or_create(
        slug=DEFAULT_SLUG,
        defaults={
            'name': 'صيف وصحة',
            'description': intro,
            'is_active': True,
            'status': 'active',
            'logo_static_path': 'img/cluster-color.png',
            'splash_static_path': 'img/asir-heritage-splash.png',
            'background_static_path': hero_image,
            'primary_color': '#15508A',
            'secondary_color': '#283A83',
            'accent_color': '#D4AF37',
            'main_title': tagline,
            'main_description': intro,
            'welcome_text': 'منطقة عسير ترحب بك',
            'doctor_settings': {'enabled': True},
            'qr_settings': {'enabled': True, 'link_version': '9'},
            'deep_link_settings': {'enabled': True},
            'page_settings': {'mobile_first': True},
        },
    )
    if not created:
        Campaign.objects.filter(pk=campaign.pk).update(is_active=True, status='active')
    Campaign.objects.exclude(pk=campaign.pk).filter(is_active=True).update(is_active=False, status='disabled')

    home_page, _ = CampaignPage.objects.get_or_create(
        campaign=campaign,
        key='home',
        defaults={
            'title': title,
            'description': intro,
            'banner_static_path': hero_image,
            'settings': {
                'tagline': tagline,
                'primary_button_label': getattr(home, 'primary_button_label', ''),
                'seasonal_alert': getattr(home, 'seasonal_alert', ''),
            },
            'active': True,
            'order': 0,
        },
    )

    for quick_button in HomeQuickButton.objects.order_by('order', 'id'):
        if CampaignButton.objects.filter(campaign=campaign, page=home_page, label=quick_button.label).exists():
            continue
        action_type = 'assistant' if quick_button.url.rstrip('/') == '/assistant' else 'page'
        CampaignButton.objects.create(
            campaign=campaign,
            page=home_page,
            label=quick_button.label,
            icon=quick_button.icon,
            order=quick_button.order,
            action_type=action_type,
            url=quick_button.url,
            active=quick_button.active,
        )

    if not CampaignButton.objects.filter(campaign=campaign, page=home_page).exists():
        CampaignButton.objects.bulk_create([
            CampaignButton(
                campaign=campaign,
                page=home_page,
                label='اسأل الدكتور مساعد',
                order=10,
                action_type='assistant',
                url='/assistant/',
                active=True,
            ),
            CampaignButton(
                campaign=campaign,
                page=home_page,
                label='قريب مني',
                order=20,
                action_type='page',
                url='/nearby/',
                active=True,
            ),
        ])

    models_to_assign = [
        ('core', 'HomeConfig'),
        ('core', 'HomeQuickButton'),
        ('core', 'FeatureFlag'),
        ('core', 'GeneralSettings'),
        ('core', 'SmartEntryConfig'),
        ('awareness', 'AwarenessContent'),
        ('awareness', 'AwarenessMessage'),
        ('assistant', 'KeywordAnswer'),
        ('assistant', 'DoctorAssistantQuestion'),
        ('events', 'HealthEvent'),
        ('locations', 'HealthLocation'),
        ('journey', 'JourneySubmission'),
        ('passport', 'PassportStamp'),
        ('passport', 'PassportAchievement'),
        ('passport', 'VisitorPassport'),
        ('qr', 'QrLocation'),
        ('qr', 'QrItem'),
        ('qr', 'QrScan'),
        ('qr', 'QrVisit'),
        ('qr', 'QrLocationVisit'),
        ('qr', 'QrVisitorProfile'),
        ('hero', 'HealthHeroQuestion'),
        ('hero', 'HealthHeroEntry'),
        ('dashboard', 'OperationLog'),
    ]
    for app_label, model_name in models_to_assign:
        model = apps.get_model(app_label, model_name)
        model.objects.filter(campaign__isnull=True).update(campaign=campaign)


def unseed_summer_health_campaign(apps, schema_editor):
    Campaign = apps.get_model('campaigns', 'Campaign')
    Campaign.objects.filter(slug=DEFAULT_SLUG).update(is_active=False, status='disabled')


class Migration(migrations.Migration):

    dependencies = [
        ('assistant', '0003_doctorassistantquestion_campaign_and_more'),
        ('awareness', '0003_awarenesscontent_campaign_awarenessmessage_campaign'),
        ('campaigns', '0001_initial'),
        ('core', '0005_featureflag_campaign_generalsettings_campaign_and_more'),
        ('dashboard', '0002_operationlog_campaign'),
        ('events', '0002_healthevent_campaign'),
        ('hero', '0003_healthheroentry_campaign_healthheroquestion_campaign'),
        ('journey', '0002_journeysubmission_campaign'),
        ('locations', '0002_healthlocation_campaign'),
        ('passport', '0002_passportachievement_campaign_passportstamp_campaign_and_more'),
        ('qr', '0004_qritem_campaign_qrlocation_campaign_and_more'),
    ]

    operations = [
        migrations.RunPython(seed_summer_health_campaign, unseed_summer_health_campaign),
    ]
