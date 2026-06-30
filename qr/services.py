from io import BytesIO
from datetime import timedelta
from urllib.parse import urlencode

import qrcode
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone

from campaigns.models import CampaignInteraction
from campaigns.services import campaign_queryset, get_active_campaign, record_campaign_interaction
from core.utils import get_visitor_id
from passport.services import award_stamp, get_or_create_passport, increment_scan

from .models import QrItem, QrLocation, QrLocationVisit, QrScan, QrVisit

QR_LINK_VERSION = '9'
SCAN_DEDUP_WINDOW = timedelta(minutes=10)

KNOWN_LOCATION_SLUGS = {
    'شارع الفن': 'art-street',
    'مطار أبها': 'abha-airport',
    'ممشى الضباب': 'fog-walkway',
    'السودة': 'soudah',
    'السودة منتزه الضباب': 'alswdh-mtnzh-aldbab',
    'مصلى العيد': 'msla-alayd',
}

RESERVED_QR_SLUGS = {
    'airport',
    'qr-airport',
    'walkway',
    'qr-walkway',
    'event',
    'qr-event',
    'booth',
    'qr-booth',
}

ARABIC_SLUG_MAP = {
    'ا': 'a',
    'أ': 'a',
    'إ': 'i',
    'آ': 'a',
    'ب': 'b',
    'ت': 't',
    'ث': 'th',
    'ج': 'j',
    'ح': 'h',
    'خ': 'kh',
    'د': 'd',
    'ذ': 'dh',
    'ر': 'r',
    'ز': 'z',
    'س': 's',
    'ش': 'sh',
    'ص': 's',
    'ض': 'd',
    'ط': 't',
    'ظ': 'z',
    'ع': 'a',
    'غ': 'gh',
    'ف': 'f',
    'ق': 'q',
    'ك': 'k',
    'ل': 'l',
    'م': 'm',
    'ن': 'n',
    'ه': 'h',
    'و': 'w',
    'ي': 'y',
    'ى': 'a',
    'ة': 'h',
    'ء': '',
    'ئ': 'e',
    'ؤ': 'o',
}


def slugify_location_name(name):
    clean_name = ' '.join((name or '').strip().split())
    if clean_name in KNOWN_LOCATION_SLUGS:
        return KNOWN_LOCATION_SLUGS[clean_name]

    slug = ''.join(ARABIC_SLUG_MAP.get(char, char) for char in clean_name).lower()
    safe = []
    previous_dash = False
    for char in slug:
        if char.isascii() and char.isalnum():
            safe.append(char)
            previous_dash = False
        elif not previous_dash:
            safe.append('-')
            previous_dash = True
    result = ''.join(safe).strip('-')[:48]
    return result or 'location'


def unique_location_slug(name, instance=None, campaign=None):
    base_slug = slugify_location_name(name)
    campaign = campaign or getattr(instance, 'campaign', None) or get_active_campaign()
    used_queryset = QrLocation.objects.exclude(pk=getattr(instance, 'pk', None))
    if campaign:
        used_queryset = used_queryset.filter(campaign=campaign)
    used = set(used_queryset.values_list('slug', flat=True))
    slug = base_slug
    suffix = 2
    while slug in used or slug in RESERVED_QR_SLUGS:
        slug = f'{base_slug}-{suffix}'
        suffix += 1
    return slug


def build_qr_location_url(request, location):
    query = urlencode({'qr': location.slug})
    return request.build_absolute_uri(f'/?{query}')


def _user_agent(request):
    return request.META.get('HTTP_USER_AGENT', '')[:260]


def _remember_start_location(request, location):
    request.session['qr_start_location_id'] = location.pk
    request.session['qr_start_location_slug'] = location.slug
    request.session['qr_start_location_name'] = location.name


def _recent_location_scan_exists(visitor_id, location):
    threshold = timezone.now() - SCAN_DEDUP_WINDOW
    return QrLocationVisit.objects.filter(
        visitor_id=visitor_id,
        qr_location=location,
        created_at__gte=threshold,
    ).exists()


def _record_location_scan(request, location):
    visitor_id = get_visitor_id(request)
    campaign = location.campaign or get_active_campaign()
    _remember_start_location(request, location)

    if _recent_location_scan_exists(visitor_id, location):
        passport = get_or_create_passport(visitor_id, campaign=campaign)
        location.refresh_from_db()
        return visitor_id, passport, False

    now = timezone.now()
    QrScan.objects.create(
        campaign=campaign,
        visitor_id=visitor_id,
        qr_type=QrScan.TYPE_LOCATION,
        path=request.get_full_path()[:240],
        qr_location=location,
        user_agent=_user_agent(request),
    )
    QrLocationVisit.objects.create(campaign=campaign, visitor_id=visitor_id, qr_location=location)
    QrLocation.objects.filter(pk=location.pk).update(scans_count=F('scans_count') + 1, last_scan_at=now)
    record_campaign_interaction(request, CampaignInteraction.TYPE_QR_SCAN, campaign=campaign, visitor_id=visitor_id, qr_location_id=location.pk)
    passport = increment_scan(visitor_id, campaign=campaign)
    location.refresh_from_db()
    return visitor_id, passport, True


def record_location_scan(request, slug):
    campaign = get_active_campaign()
    location = get_object_or_404(campaign_queryset(QrLocation.objects.filter(slug=slug, active=True), campaign=campaign))
    visitor_id, passport, counted = _record_location_scan(request, location)
    return {
        'visitor_id': visitor_id,
        'location': location,
        'passport': passport,
        'stamp_awarded': False,
        'counted': counted,
        'duplicate': not counted,
    }


def record_home_qr_scan(request, slug):
    visitor_id = get_visitor_id(request)
    campaign = get_active_campaign()
    location = campaign_queryset(QrLocation.objects.filter(slug=slug, active=True), campaign=campaign).first()
    if not location:
        return {
            'visitor_id': visitor_id,
            'location': None,
            'passport': get_or_create_passport(visitor_id, campaign=campaign),
            'stamp_awarded': False,
            'counted': False,
            'duplicate': False,
        }

    visitor_id, passport, counted = _record_location_scan(request, location)
    return {
        'visitor_id': visitor_id,
        'location': location,
        'passport': passport,
        'stamp_awarded': False,
        'counted': counted,
        'duplicate': not counted,
    }


def record_item_scan(request, item_id):
    visitor_id = get_visitor_id(request)
    campaign = get_active_campaign()
    item = get_object_or_404(campaign_queryset(QrItem.objects.filter(pk=item_id, active=True), campaign=campaign))
    campaign = item.campaign or campaign

    QrScan.objects.create(
        campaign=campaign,
        visitor_id=visitor_id,
        qr_type=QrScan.TYPE_ITEM,
        path=request.get_full_path()[:240],
        qr_item=item,
        user_agent=_user_agent(request),
    )
    QrVisit.objects.create(campaign=campaign, visitor_id=visitor_id, qr_item=item)
    QrItem.objects.filter(pk=item.pk).update(scans_count=F('scans_count') + 1)
    record_campaign_interaction(request, CampaignInteraction.TYPE_QR_SCAN, campaign=campaign, visitor_id=visitor_id, qr_item_id=item.pk)
    increment_scan(visitor_id, campaign=campaign)
    passport, awarded = award_stamp(visitor_id, item.stamp, campaign=campaign)
    item.refresh_from_db()
    return {
        'visitor_id': visitor_id,
        'item': item,
        'passport': passport,
        'stamp_awarded': awarded,
    }


def generate_qr_png(url, box_size=24, border=8):
    image = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=box_size,
        border=border,
    )
    image.add_data(url)
    image.make(fit=True)
    image = image.make_image(fill_color='#15508A', back_color='white').convert('RGB')
    buffer = BytesIO()
    image.save(buffer, format='PNG', optimize=False)
    return buffer.getvalue()
