from django.db.models import Count
from django.db.models import Q

from core.utils import get_visitor_id

from .models import Campaign, CampaignInteraction, CampaignPage


DEFAULT_CAMPAIGN_SLUG = 'summer-health'


def get_active_campaign():
    campaign = Campaign.objects.filter(is_active=True, status=Campaign.STATUS_ACTIVE).order_by('-updated_at').first()
    if campaign:
        return campaign
    return Campaign.objects.exclude(status=Campaign.STATUS_ARCHIVED).order_by('-is_active', 'created_at').first()


def get_default_campaign():
    return Campaign.objects.filter(slug=DEFAULT_CAMPAIGN_SLUG).first() or get_active_campaign()


def get_campaign_home_page(campaign=None):
    campaign = campaign or get_active_campaign()
    if not campaign:
        return None
    return campaign.pages.filter(key=CampaignPage.PAGE_HOME, active=True).first()


def campaign_queryset(queryset, campaign=None):
    campaign = campaign or get_active_campaign()
    if not campaign:
        return queryset
    model = queryset.model
    if not any(field.name == 'campaign' for field in model._meta.fields):
        return queryset
    return queryset.filter(Q(campaign=campaign) | Q(campaign__isnull=True))


def record_campaign_interaction(request, event_type, campaign=None, visitor_id=None, **metadata):
    campaign = campaign or get_active_campaign()
    if visitor_id is None:
        visitor_id = get_visitor_id(request)
    return CampaignInteraction.objects.create(
        campaign=campaign,
        event_type=event_type,
        visitor_id=visitor_id or '',
        path=request.get_full_path()[:240] if request else '',
        metadata=metadata,
    )


def campaign_stats(campaign=None):
    interactions = CampaignInteraction.objects.all()
    if campaign:
        interactions = interactions.filter(campaign=campaign)
    grouped = {
        row['event_type']: row['total']
        for row in interactions.values('event_type').annotate(total=Count('id'))
    }

    from hero.models import HealthHeroEntry
    from journey.models import JourneySubmission
    from qr.models import QrScan

    qr_scans = QrScan.objects.all()
    journeys = JourneySubmission.objects.all()
    hero_entries = HealthHeroEntry.objects.all()
    if campaign:
        qr_scans = qr_scans.filter(campaign=campaign)
        journeys = journeys.filter(campaign=campaign)
        hero_entries = hero_entries.filter(campaign=campaign)

    visitor_ids = set(interactions.exclude(visitor_id='').values_list('visitor_id', flat=True))
    visitor_ids.update(qr_scans.exclude(visitor_id='').values_list('visitor_id', flat=True))
    visitor_ids.update(journeys.exclude(visitor_id='').values_list('visitor_id', flat=True))
    visitor_ids.update(hero_entries.exclude(visitor_id='').values_list('visitor_id', flat=True))

    return {
        'visitors': len(visitor_ids),
        'qr_scans': qr_scans.count(),
        'interactions': grouped.get(CampaignInteraction.TYPE_INTERACTION, 0)
        + grouped.get(CampaignInteraction.TYPE_ASSISTANT_QUERY, 0)
        + journeys.count()
        + hero_entries.count(),
        'assistant_opens': grouped.get(CampaignInteraction.TYPE_ASSISTANT_OPEN, 0),
        'total_events': sum(grouped.values()),
    }
