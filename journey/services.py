from events.models import HealthEvent
from locations.models import HealthLocation


def _older_adult(answers):
    return answers.get('age_group') in {'senior', 'elderly'}


def _first_or_none(queryset):
    return queryset.first()


def _pick_event(answers):
    events = HealthEvent.objects.filter(active=True).order_by('order', 'date')
    if answers.get('party_type') == 'family' or answers.get('visit_purpose') == 'family':
        family_event = events.filter(category__icontains='عائل').first()
        if family_event:
            return family_event
    if answers.get('visit_purpose') in {'sport', 'hiking'}:
        sport_event = events.filter(category__icontains='نشاط').first()
        if sport_event:
            return sport_event
    if _older_adult(answers) or answers.get('has_health_condition'):
        awareness_event = events.filter(category__icontains='توعية').first()
        if awareness_event:
            return awareness_event
    return _first_or_none(events)


def _pick_location(answers, location_type):
    locations = HealthLocation.objects.filter(active=True, location_type=location_type)
    if answers.get('current_location') == 'soudah':
        preferred = locations.filter(city__icontains='السودة').first()
        if preferred:
            return preferred
    return locations.order_by('order', 'id').first()


def build_daily_plan(answers):
    urgent = answers.get('visit_purpose') == 'urgent' or answers.get('has_health_condition')
    health_center = _pick_location(answers, HealthLocation.TYPE_EMERGENCY if urgent else HealthLocation.TYPE_HEALTH_CENTER)
    walkway = _pick_location(answers, HealthLocation.TYPE_WALKWAY)
    event = _pick_event(answers)

    if urgent:
        return {
            'title': 'خطة أمان فورية',
            'summary': 'الأولوية الآن هي الوصول للمساعدة الصحية وعدم تأجيل الأعراض.',
            'risk_level': 'عاجل',
            'event': event,
            'health_center': health_center,
            'walkway': None,
            'tips': [
                'اتصل بالإسعاف 997 عند وجود ألم صدر أو صعوبة تنفس أو نزيف.',
                'اتصل بـ 937 للاستشارة الصحية عند الحاجة.',
                'توجه لأقرب طوارئ ولا تبدأ أي نشاط بدني حتى تطمئن.',
            ],
            'actions': [
                {'label': 'اتصال 997', 'url': 'tel:997'},
                {'label': 'اتصال 937', 'url': 'tel:937'},
            ],
        }

    tips = [
        'اشرب الماء على دفعات منتظمة قبل الشعور بالعطش.',
        'اختر وقتا معتدلا للنشاط وتجنب الشمس المباشرة وقت الظهيرة.',
        'احتفظ برقم 937 للاستشارة الصحية أثناء الرحلة.',
    ]

    if _older_adult(answers):
        tips = [
            'اختر مسارا قصيرا ومظللا واجعل أقرب مركز صحي ضمن خطتك.',
            'خذ استراحة كل 15 دقيقة واشرب الماء على دفعات.',
            'تجنب الجهد العالي وتوقف عند الدوخة أو ألم الصدر.',
        ]
    elif answers.get('party_type') == 'family':
        tips = [
            'ابدأ بموقع قريب من الخدمات ومناسب للأطفال وكبار السن.',
            'اتفق مع العائلة على نقطة تجمع واضحة.',
            'احمل ماء ووجبة خفيفة وخطط لاستراحات قصيرة.',
        ]
    elif answers.get('visit_purpose') == 'hiking':
        tips = [
            'اختر مسارا معروفا ولا تذهب وحدك.',
            'احمل ماء كافيا واستخدم واقي الشمس وحذاء مناسبا.',
            'توقف فورا عند ألم الصدر أو ضيق التنفس واطلب المساعدة.',
        ]

    return {
        'title': 'خطة صحية ليومك في عسير',
        'summary': 'اقتراحات خفيفة تربط وجهتك بنشاط آمن وموقع صحي قريب.',
        'risk_level': 'اعتيادي',
        'event': event,
        'health_center': health_center,
        'walkway': walkway,
        'tips': tips,
        'actions': [
            {'label': 'عرض المواقع القريبة', 'url': '/nearby/'},
            {'label': 'عرض الفعاليات', 'url': '/events/'},
        ],
    }
