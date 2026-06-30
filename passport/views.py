from django.shortcuts import render

from core.utils import get_visitor_id
from qr.models import QrLocationVisit, QrVisit

from .models import PassportAchievement
from .services import active_stamps, get_or_create_passport


def passport_view(request):
    visitor_id = get_visitor_id(request)
    passport = get_or_create_passport(visitor_id)
    available_achievements = PassportAchievement.objects.filter(active=True)
    item_visits = QrVisit.objects.filter(visitor_id=visitor_id).select_related('qr_item').order_by('-created_at')[:8]
    location_visits = QrLocationVisit.objects.filter(visitor_id=visitor_id).select_related('qr_location').order_by('-created_at')[:8]
    whatsapp_text = f'أنجزت {passport.points} نقطة في جواز صحة عسير عبر منصة صيف وصحة - مساعد'

    return render(
        request,
        'passport/passport.html',
        {
            'passport': passport,
            'all_stamps': active_stamps(),
            'available_achievements': available_achievements,
            'collected_stamp_ids': set(passport.stamps.values_list('id', flat=True)),
            'achievement_ids': set(passport.achievements.values_list('id', flat=True)),
            'item_visits': item_visits,
            'location_visits': location_visits,
            'whatsapp_text': whatsapp_text,
        },
    )

# Create your views here.
