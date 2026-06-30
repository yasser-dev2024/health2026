from django.contrib import messages as django_messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Count, Max, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from campaigns.services import campaign_queryset, campaign_stats, get_active_campaign
from awareness.forms import AwarenessContentForm, AwarenessMessageForm
from awareness.models import AwarenessContent, AwarenessMessage
from events.forms import HealthEventForm
from events.models import HealthEvent
from hero.models import HealthHeroEntry, HealthHeroQuestion
from journey.models import JourneySubmission
from locations.forms import HealthLocationForm
from locations.models import HealthLocation
from passport.models import PassportStamp, VisitorPassport
from qr.forms import QrLocationForm
from qr.models import QrItem, QrLocation, QrLocationVisit, QrScan, QrVisitorProfile
from qr.services import build_qr_location_url, generate_qr_png

from .models import OperationLog
from .services import log_operation


class AdminLoginView(LoginView):
    template_name = 'dashboard/login.html'
    redirect_authenticated_user = True


def logout_view(request):
    logout(request)
    return redirect('core:home')


METRIC_LABELS = {
    'events': ('الفعاليات', '📅', 'metric-teal'),
    'locations': ('المواقع الصحية', '📍', 'metric-green'),
    'messages': ('الرسائل التوعوية', '💬', 'metric-purple'),
    'downloads': ('مواد التحميل', '📥', 'metric-gold'),
    'journeys': ('خطط الرحلة', '🗺️', 'metric-slate'),
    'qr_scans': ('مسحات QR', '📷', ''),
    'passport_users': ('مستخدمو الجواز', '🎫', 'metric-rose'),
    'hero_entries': ('متسابقو بطل الصحة', '🏆', 'metric-gold'),
}


@login_required
def dashboard_view(request):
    campaign = get_active_campaign()
    today = timezone.localdate()
    week_start = today - timezone.timedelta(days=6)
    month_start = today.replace(day=1)

    raw_metrics = {
        'events': campaign_queryset(HealthEvent.objects.all(), campaign=campaign).count(),
        'locations': campaign_queryset(HealthLocation.objects.all(), campaign=campaign).count(),
        'messages': campaign_queryset(AwarenessMessage.objects.all(), campaign=campaign).count(),
        'downloads': campaign_queryset(AwarenessContent.objects.all(), campaign=campaign).count(),
        'journeys': campaign_queryset(JourneySubmission.objects.all(), campaign=campaign).count(),
        'qr_scans': campaign_queryset(QrScan.objects.all(), campaign=campaign).count(),
        'passport_users': campaign_queryset(VisitorPassport.objects.all(), campaign=campaign).count(),
        'hero_entries': campaign_queryset(HealthHeroEntry.objects.all(), campaign=campaign).count(),
    }

    metrics = [
        {
            'key': key,
            'label': METRIC_LABELS[key][0],
            'icon': METRIC_LABELS[key][1],
            'color_class': METRIC_LABELS[key][2],
            'value': value,
        }
        for key, value in raw_metrics.items()
    ]

    qr_visits = campaign_queryset(QrLocationVisit.objects.all(), campaign=campaign)
    qr_today = qr_visits.filter(created_at__date=today).count()
    qr_week = qr_visits.filter(created_at__date__gte=week_start).count()
    qr_month = qr_visits.filter(created_at__date__gte=month_start).count()
    qr_total = qr_visits.count()
    qr_visitors = qr_visits.values('visitor_id').distinct().count()

    top_downloads = list(
        campaign_queryset(AwarenessContent.objects.filter(active=True, download_count__gt=0), campaign=campaign)
        .order_by('-download_count')[:6]
    )
    total_downloads_count = campaign_queryset(AwarenessContent.objects.filter(active=True), campaign=campaign).aggregate(
        total=Sum('download_count')
    )['total'] or 0

    top_qr_locations = list(
        campaign_queryset(QrLocation.objects.all(), campaign=campaign).annotate(visit_total=Count('visits'))
        .order_by('-visit_total')[:6]
    )
    chart_total = sum(loc.visit_total for loc in top_qr_locations) or 1

    age_series = _choice_series(QrVisitorProfile, 'age_group', QrVisitorProfile.AGE_GROUP_CHOICES, campaign=campaign)
    visitor_type_series = _choice_series(QrVisitorProfile, 'visitor_type', QrVisitorProfile.VISITOR_TYPE_CHOICES, campaign=campaign)

    # Downloads by type
    dl_type_series = []
    for value, label in AwarenessContent.TYPE_CHOICES:
        count = campaign_queryset(AwarenessContent.objects.filter(content_type=value, active=True), campaign=campaign).count()
        if count:
            dl_type_series.append({'label': label, 'count': count})

    # Events by category
    events_series = list(
        campaign_queryset(HealthEvent.objects.all(), campaign=campaign).values('category')
        .annotate(count=Count('id'))
        .order_by('-count')[:6]
    )

    # Locations by type
    loc_series = []
    for value, label in HealthLocation.TYPE_CHOICES:
        count = campaign_queryset(HealthLocation.objects.filter(location_type=value), campaign=campaign).count()
        if count:
            loc_series.append({'label': label, 'count': count})

    admin_nav = [
        {'label': 'المؤشرات', 'url': '/admin/', 'icon': '▦'},
        {'label': 'مكتبة التحميلات', 'url': '/admin/downloads/', 'icon': '📥'},
        {'label': 'الرسائل التوعوية', 'url': '/admin/messages/', 'icon': '💬'},
        {'label': 'الفعاليات الصحية', 'url': '/admin/events/', 'icon': '📅'},
        {'label': 'المواقع الصحية', 'url': '/admin/locations/', 'icon': '📍'},
        {'label': 'إدارة QR', 'url': '/admin/qr-locations/', 'icon': 'QR'},
    ]

    qr_locations_qs = campaign_queryset(QrLocation.objects.all(), campaign=campaign)
    qr_locations_total = qr_locations_qs.count()
    qr_active_count = qr_locations_qs.filter(active=True).count()
    qr_inactive_count = qr_locations_qs.filter(active=False).count()
    qr_most_used = (
        campaign_queryset(QrLocation.objects.all(), campaign=campaign).annotate(visit_total=Count('visits'))
        .order_by('-visit_total', '-scans_count')
        .first()
    )
    qr_recent = qr_locations_qs.order_by('-created_at').first()

    return render(request, 'dashboard/index.html', {
        'active_campaign': campaign,
        'campaign_stats': campaign_stats(campaign),
        'metrics': metrics,
        'admin_nav': admin_nav,
        'recent_scans': campaign_queryset(QrScan.objects.select_related('qr_location', 'qr_item'), campaign=campaign).order_by('-created_at')[:10],
        'recent_logs': campaign_queryset(OperationLog.objects.select_related('user'), campaign=campaign).order_by('-created_at')[:10],
        'qr_stats': {
            'today': qr_today, 'week': qr_week,
            'month': qr_month, 'total': qr_total, 'visitors': qr_visitors,
        },
        'qr_locations_stats': {
            'total': qr_locations_total,
            'active': qr_active_count,
            'inactive': qr_inactive_count,
            'most_used': qr_most_used,
            'recent': qr_recent,
        },
        'top_downloads': top_downloads,
        'total_downloads_count': total_downloads_count,
        'top_qr_locations': top_qr_locations,
        'chart_total': chart_total,
        'age_series': age_series,
        'visitor_type_series': visitor_type_series,
        'dl_type_series': dl_type_series,
        'events_series': events_series,
        'loc_series': loc_series,
    })


def _choice_series(model, field_name, choices, campaign=None):
    rows = (
        campaign_queryset(model.objects.exclude(**{field_name: ''}), campaign=campaign)
        .values(field_name)
        .annotate(total=Count('id'))
        .order_by()
    )
    counts = {row[field_name]: row['total'] for row in rows}
    total = sum(counts.values()) or 1
    return [
        {
            'label': label,
            'count': counts.get(value, 0),
            'percent': round((counts.get(value, 0) / total) * 100),
        }
        for value, label in choices
        if counts.get(value, 0)
    ]


def _location_usage_series(locations, total_scans):
    denominator = total_scans or 1
    return [
        {
            'label': location.name,
            'count': location.visit_total,
            'percent': round((location.visit_total / denominator) * 100),
        }
        for location in locations
        if location.visit_total
    ]


# ─────────────────────────────────────────
#  DOWNLOADS MANAGEMENT
# ─────────────────────────────────────────
@login_required
def admin_downloads_view(request):
    campaign = get_active_campaign()
    editing = None
    if request.GET.get('edit'):
        editing = campaign_queryset(AwarenessContent.objects.filter(pk=request.GET['edit']), campaign=campaign).first()

    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        item_id = request.POST.get('item_id')
        item = campaign_queryset(AwarenessContent.objects.filter(pk=item_id), campaign=campaign).first() if item_id else None

        if action == 'delete' and item:
            title = item.title
            item.delete()
            log_operation(request, 'التحميلات', f'حذف: {title}')
            django_messages.success(request, f'تم حذف "{title}"')
            return redirect('admin_downloads')

        if action == 'toggle' and item:
            item.active = not item.active
            item.save(update_fields=['active', 'updated_at'])
            log_operation(request, 'التحميلات', f'تغيير حالة: {item.title}')
            return redirect('admin_downloads')

        if action == 'order_up' and item:
            prev = campaign_queryset(AwarenessContent.objects.filter(order__lt=item.order), campaign=campaign).order_by('-order').first()
            if prev:
                item.order, prev.order = prev.order, item.order
                item.save(update_fields=['order'])
                prev.save(update_fields=['order'])
            return redirect('admin_downloads')

        if action == 'order_down' and item:
            nxt = campaign_queryset(AwarenessContent.objects.filter(order__gt=item.order), campaign=campaign).order_by('order').first()
            if nxt:
                item.order, nxt.order = nxt.order, item.order
                item.save(update_fields=['order'])
                nxt.save(update_fields=['order'])
            return redirect('admin_downloads')

        form = AwarenessContentForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            saved = form.save(commit=False)
            if not saved.campaign_id:
                saved.campaign = campaign
            saved.save()
            form.save_m2m()
            log_operation(request, 'التحميلات', f'حفظ: {saved.title}')
            django_messages.success(request, f'تم حفظ "{saved.title}"')
            return redirect('admin_downloads')
        editing = item
    else:
        form = AwarenessContentForm(instance=editing)

    items = campaign_queryset(AwarenessContent.objects.all(), campaign=campaign).order_by('order', 'title')
    total_dl = items.aggregate(t=Sum('download_count'))['t'] or 0
    type_counts = {}
    for v, lbl in AwarenessContent.TYPE_CHOICES:
        type_counts[v] = {'label': lbl, 'count': items.filter(content_type=v).count()}
    top_items = list(items.filter(download_count__gt=0).order_by('-download_count')[:8])
    max_dl = top_items[0].download_count if top_items else 1

    return render(request, 'dashboard/admin_downloads.html', {
        'form': form,
        'editing': editing,
        'items': items,
        'total_dl': total_dl,
        'type_counts': type_counts,
        'top_items': top_items,
        'max_dl': max_dl,
        'active_count': items.filter(active=True).count(),
        'inactive_count': items.filter(active=False).count(),
    })


# ─────────────────────────────────────────
#  MESSAGES MANAGEMENT
# ─────────────────────────────────────────
@login_required
def admin_messages_view(request):
    campaign = get_active_campaign()
    editing = None
    if request.GET.get('edit'):
        editing = campaign_queryset(AwarenessMessage.objects.filter(pk=request.GET['edit']), campaign=campaign).first()

    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        item_id = request.POST.get('item_id')
        item = campaign_queryset(AwarenessMessage.objects.filter(pk=item_id), campaign=campaign).first() if item_id else None

        if action == 'delete' and item:
            title = item.title
            item.delete()
            log_operation(request, 'الرسائل', f'حذف: {title}')
            django_messages.success(request, f'تم حذف "{title}"')
            return redirect('admin_messages')

        if action == 'toggle' and item:
            item.active = not item.active
            item.save(update_fields=['active', 'updated_at'])
            return redirect('admin_messages')

        if action == 'order_up' and item:
            prev = campaign_queryset(AwarenessMessage.objects.filter(order__lt=item.order), campaign=campaign).order_by('-order').first()
            if prev:
                item.order, prev.order = prev.order, item.order
                item.save(update_fields=['order'])
                prev.save(update_fields=['order'])
            return redirect('admin_messages')

        if action == 'order_down' and item:
            nxt = campaign_queryset(AwarenessMessage.objects.filter(order__gt=item.order), campaign=campaign).order_by('order').first()
            if nxt:
                item.order, nxt.order = nxt.order, item.order
                item.save(update_fields=['order'])
                nxt.save(update_fields=['order'])
            return redirect('admin_messages')

        form = AwarenessMessageForm(request.POST, instance=item)
        if form.is_valid():
            saved = form.save(commit=False)
            if not saved.campaign_id:
                saved.campaign = campaign
            saved.save()
            form.save_m2m()
            log_operation(request, 'الرسائل', f'حفظ: {saved.title}')
            django_messages.success(request, f'تم حفظ "{saved.title}"')
            return redirect('admin_messages')
        editing = item
    else:
        form = AwarenessMessageForm(instance=editing)

    items = campaign_queryset(AwarenessMessage.objects.all(), campaign=campaign).order_by('order', 'id')
    categories = list(items.values('category').annotate(count=Count('id')).order_by('-count'))

    return render(request, 'dashboard/admin_messages.html', {
        'form': form,
        'editing': editing,
        'items': items,
        'categories': categories,
        'active_count': items.filter(active=True).count(),
        'inactive_count': items.filter(active=False).count(),
    })


# ─────────────────────────────────────────
#  EVENTS MANAGEMENT
# ─────────────────────────────────────────
@login_required
def admin_events_view(request):
    campaign = get_active_campaign()
    editing = None
    if request.GET.get('edit'):
        editing = campaign_queryset(HealthEvent.objects.filter(pk=request.GET['edit']), campaign=campaign).first()

    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        item_id = request.POST.get('item_id')
        item = campaign_queryset(HealthEvent.objects.filter(pk=item_id), campaign=campaign).first() if item_id else None

        if action == 'delete' and item:
            title = item.title
            item.delete()
            log_operation(request, 'الفعاليات', f'حذف: {title}')
            django_messages.success(request, f'تم حذف "{title}"')
            return redirect('admin_events')

        if action == 'toggle' and item:
            item.active = not item.active
            item.save(update_fields=['active', 'updated_at'])
            return redirect('admin_events')

        if action == 'toggle_home' and item:
            item.show_on_home = not item.show_on_home
            item.save(update_fields=['show_on_home', 'updated_at'])
            return redirect('admin_events')

        if action == 'order_up' and item:
            prev = campaign_queryset(HealthEvent.objects.filter(order__lt=item.order), campaign=campaign).order_by('-order').first()
            if prev:
                item.order, prev.order = prev.order, item.order
                item.save(update_fields=['order'])
                prev.save(update_fields=['order'])
            return redirect('admin_events')

        if action == 'order_down' and item:
            nxt = campaign_queryset(HealthEvent.objects.filter(order__gt=item.order), campaign=campaign).order_by('order').first()
            if nxt:
                item.order, nxt.order = nxt.order, item.order
                item.save(update_fields=['order'])
                nxt.save(update_fields=['order'])
            return redirect('admin_events')

        form = HealthEventForm(request.POST, instance=item)
        if form.is_valid():
            saved = form.save(commit=False)
            if not saved.campaign_id:
                saved.campaign = campaign
            saved.save()
            form.save_m2m()
            log_operation(request, 'الفعاليات', f'حفظ: {saved.title}')
            django_messages.success(request, f'تم حفظ "{saved.title}"')
            return redirect('admin_events')
        editing = item
    else:
        form = HealthEventForm(instance=editing)

    items = campaign_queryset(HealthEvent.objects.all(), campaign=campaign).order_by('order', 'date', 'time')
    total_visits = items.aggregate(t=Sum('visits'))['t'] or 0
    cat_series = list(items.values('category').annotate(count=Count('id')).order_by('-count')[:6])
    city_series = list(items.values('city').annotate(count=Count('id')).order_by('-count')[:6])
    top_visited = list(items.filter(visits__gt=0).order_by('-visits')[:6])
    max_visits = top_visited[0].visits if top_visited else 1

    return render(request, 'dashboard/admin_events.html', {
        'form': form,
        'editing': editing,
        'items': items,
        'total_visits': total_visits,
        'cat_series': cat_series,
        'city_series': city_series,
        'top_visited': top_visited,
        'max_visits': max_visits,
        'active_count': items.filter(active=True).count(),
        'inactive_count': items.filter(active=False).count(),
        'home_count': items.filter(show_on_home=True).count(),
    })


# ─────────────────────────────────────────
#  LOCATIONS MANAGEMENT
# ─────────────────────────────────────────
@login_required
def admin_locations_view(request):
    campaign = get_active_campaign()
    editing = None
    if request.GET.get('edit'):
        editing = campaign_queryset(HealthLocation.objects.filter(pk=request.GET['edit']), campaign=campaign).first()

    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        item_id = request.POST.get('item_id')
        item = campaign_queryset(HealthLocation.objects.filter(pk=item_id), campaign=campaign).first() if item_id else None

        if action == 'delete' and item:
            name = item.name
            item.delete()
            log_operation(request, 'المواقع', f'حذف: {name}')
            django_messages.success(request, f'تم حذف "{name}"')
            return redirect('admin_locations')

        if action == 'toggle' and item:
            item.active = not item.active
            item.save(update_fields=['active', 'updated_at'])
            return redirect('admin_locations')

        if action == 'order_up' and item:
            prev = campaign_queryset(HealthLocation.objects.filter(order__lt=item.order), campaign=campaign).order_by('-order').first()
            if prev:
                item.order, prev.order = prev.order, item.order
                item.save(update_fields=['order'])
                prev.save(update_fields=['order'])
            return redirect('admin_locations')

        if action == 'order_down' and item:
            nxt = campaign_queryset(HealthLocation.objects.filter(order__gt=item.order), campaign=campaign).order_by('order').first()
            if nxt:
                item.order, nxt.order = nxt.order, item.order
                item.save(update_fields=['order'])
                nxt.save(update_fields=['order'])
            return redirect('admin_locations')

        form = HealthLocationForm(request.POST, instance=item)
        if form.is_valid():
            saved = form.save(commit=False)
            if not saved.campaign_id:
                saved.campaign = campaign
            saved.save()
            form.save_m2m()
            log_operation(request, 'المواقع', f'حفظ: {saved.name}')
            django_messages.success(request, f'تم حفظ "{saved.name}"')
            return redirect('admin_locations')
        editing = item
    else:
        form = HealthLocationForm(instance=editing)

    items = campaign_queryset(HealthLocation.objects.all(), campaign=campaign).order_by('order', 'city', 'name')
    type_series = []
    for v, lbl in HealthLocation.TYPE_CHOICES:
        count = items.filter(location_type=v).count()
        type_series.append({'label': lbl, 'value': v, 'count': count})
    city_series = list(items.values('city').annotate(count=Count('id')).order_by('-count')[:8])
    max_type_count = max((s['count'] for s in type_series), default=1)

    return render(request, 'dashboard/admin_locations.html', {
        'form': form,
        'editing': editing,
        'items': items,
        'type_series': type_series,
        'city_series': city_series,
        'max_type_count': max_type_count,
        'active_count': items.filter(active=True).count(),
        'inactive_count': items.filter(active=False).count(),
    })


# ─────────────────────────────────────────
#  QR LOCATIONS (existing, kept)
# ─────────────────────────────────────────
@login_required
def qr_locations_view(request):
    editing_location = None
    if request.GET.get('edit'):
        editing_location = QrLocation.objects.filter(pk=request.GET.get('edit')).first()

    form = QrLocationForm(instance=editing_location)

    if request.method == 'POST':
        action = request.POST.get('action', 'save')
        location = None
        if request.POST.get('location_id'):
            location = QrLocation.objects.filter(pk=request.POST.get('location_id')).first()

        if action == 'delete' and location:
            location_name = location.name
            location.delete()
            log_operation(request, 'إدارة QR', f'تم حذف موقع QR: {location_name}')
            django_messages.success(request, 'تم حذف موقع QR.')
            return redirect('admin_qr_locations')

        if action == 'toggle' and location:
            location.active = not location.active
            location.save(update_fields=['active', 'updated_at'])
            state = 'تفعيل' if location.active else 'تعطيل'
            log_operation(request, 'إدارة QR', f'تم {state} موقع QR: {location.name}')
            django_messages.success(request, f'تم {state} موقع QR.')
            return redirect('admin_qr_locations')

        form = QrLocationForm(request.POST, instance=location)
        if form.is_valid():
            location = form.save()
            log_operation(request, 'إدارة QR', f'تم حفظ موقع QR: {location.name}')
            django_messages.success(request, 'تم حفظ موقع QR وتحديث الرابط.')
            return redirect('admin_qr_locations')
        editing_location = location

    today = timezone.localdate()
    week_start = today - timezone.timedelta(days=6)
    month_start = today.replace(day=1)
    locations = list(
        QrLocation.objects.annotate(
            visit_total=Count('visits'),
            latest_scan=Max('visits__created_at'),
        ).order_by('city', 'name')
    )
    locations_with_links = [
        {
            'object': location,
            'qr_url': build_qr_location_url(request, location),
            'png_url': reverse('admin_qr_location_png', kwargs={'location_id': location.id}),
            'png_download_url': f"{reverse('admin_qr_location_png', kwargs={'location_id': location.id})}?download=1",
        }
        for location in locations
    ]
    total_scans = QrLocationVisit.objects.count()
    scans_today = QrLocationVisit.objects.filter(created_at__date=today).count()
    scans_week = QrLocationVisit.objects.filter(created_at__date__gte=week_start).count()
    scans_month = QrLocationVisit.objects.filter(created_at__date__gte=month_start).count()
    total_visitors = QrLocationVisit.objects.values('visitor_id').distinct().count()
    top_locations = list(
        QrLocation.objects.annotate(
            visit_total=Count('visits'),
            latest_scan=Max('visits__created_at'),
        ).order_by('-visit_total', '-scans_count', 'name')[:8]
    )
    least_scanned = (
        QrLocation.objects.annotate(visit_total=Count('visits'))
        .order_by('visit_total', 'name')
        .first()
    )
    last_scan = QrLocationVisit.objects.select_related('qr_location').order_by('-created_at').first()

    return render(request, 'dashboard/qr_locations.html', {
        'form': form,
        'editing_location': editing_location,
        'locations': locations_with_links,
        'items': QrItem.objects.order_by('title'),
        'scans': QrScan.objects.select_related('qr_location', 'qr_item').order_by('-created_at')[:30],
        'scan_log_rows': QrScan.objects.select_related('qr_location', 'qr_item').order_by('-created_at')[:50],
        'qr_stats': {
            'total_created': len(locations),
            'total_scans': total_scans,
            'total_visitors': total_visitors,
            'scans_today': scans_today,
            'scans_week': scans_week,
            'scans_month': scans_month,
            'most_scanned': top_locations[0] if top_locations else None,
            'least_scanned': least_scanned,
            'last_scan': last_scan,
            'top_locations': top_locations,
            'chart_total': total_scans or 1,
        },
        'analytics': {
            'age_groups': _choice_series(QrVisitorProfile, 'age_group', QrVisitorProfile.AGE_GROUP_CHOICES),
            'health_topics': _choice_series(QrVisitorProfile, 'health_topic', QrVisitorProfile.HEALTH_TOPIC_CHOICES),
            'visitor_types': _choice_series(QrVisitorProfile, 'visitor_type', QrVisitorProfile.VISITOR_TYPE_CHOICES),
            'party_types': _choice_series(QrVisitorProfile, 'party_type', QrVisitorProfile.PARTY_TYPE_CHOICES),
            'location_usage': _location_usage_series(top_locations, total_scans),
        },
    })


@login_required
def qr_location_png_view(request, location_id):
    location = get_object_or_404(QrLocation, pk=location_id)
    url = build_qr_location_url(request, location)
    image_bytes = generate_qr_png(url)
    response = HttpResponse(image_bytes, content_type='image/png')
    disposition = 'attachment' if request.GET.get('download') == '1' else 'inline'
    response['Content-Disposition'] = f'{disposition}; filename="qr-{location.slug}-print.png"'
    return response
