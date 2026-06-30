from django.db import transaction
from django.db.models import F

from campaigns.services import get_active_campaign

from .models import PassportAchievement, PassportStamp, VisitorPassport


def get_or_create_passport(visitor_id, campaign=None):
    campaign = campaign or get_active_campaign()
    passport, _ = VisitorPassport.objects.get_or_create(campaign=campaign, visitor_id=visitor_id)
    return passport


def increment_scan(visitor_id, campaign=None):
    passport = get_or_create_passport(visitor_id, campaign=campaign)
    VisitorPassport.objects.filter(pk=passport.pk).update(scans_count=F('scans_count') + 1)
    passport.refresh_from_db()
    unlock_achievements(passport)
    return passport


def unlock_achievements(passport):
    stamp_count = passport.stamps.count()
    achievements = PassportAchievement.objects.filter(
        campaign=passport.campaign,
        active=True,
        required_points__lte=passport.points,
        required_stamps__lte=stamp_count,
    )
    for achievement in achievements:
        passport.achievements.add(achievement)
    return passport.achievements.count()


@transaction.atomic
def award_stamp(visitor_id, stamp, campaign=None):
    campaign = campaign or getattr(stamp, 'campaign', None) or get_active_campaign()
    if not stamp or not stamp.active:
        return get_or_create_passport(visitor_id, campaign=campaign), False

    passport = get_or_create_passport(visitor_id, campaign=campaign)
    if passport.stamps.filter(pk=stamp.pk).exists():
        unlock_achievements(passport)
        return passport, False

    passport.stamps.add(stamp)
    VisitorPassport.objects.filter(pk=passport.pk).update(points=F('points') + stamp.points)
    passport.refresh_from_db()
    unlock_achievements(passport)
    return passport, True


def active_stamps():
    campaign = get_active_campaign()
    queryset = PassportStamp.objects.filter(active=True)
    if campaign:
        queryset = queryset.filter(campaign=campaign)
    return queryset.order_by('name')
