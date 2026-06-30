from datetime import date

from django.db import migrations


def seed_data(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    HomeConfig = apps.get_model('core', 'HomeConfig')
    HomeQuickButton = apps.get_model('core', 'HomeQuickButton')
    FeatureFlag = apps.get_model('core', 'FeatureFlag')
    GeneralSettings = apps.get_model('core', 'GeneralSettings')
    SmartEntryConfig = apps.get_model('core', 'SmartEntryConfig')
    HealthEvent = apps.get_model('events', 'HealthEvent')
    HealthLocation = apps.get_model('locations', 'HealthLocation')
    AwarenessContent = apps.get_model('awareness', 'AwarenessContent')
    AwarenessMessage = apps.get_model('awareness', 'AwarenessMessage')
    KeywordAnswer = apps.get_model('assistant', 'KeywordAnswer')
    DoctorAssistantQuestion = apps.get_model('assistant', 'DoctorAssistantQuestion')
    PassportStamp = apps.get_model('passport', 'PassportStamp')
    PassportAchievement = apps.get_model('passport', 'PassportAchievement')
    QrLocation = apps.get_model('qr', 'QrLocation')
    QrItem = apps.get_model('qr', 'QrItem')
    HealthHeroQuestion = apps.get_model('hero', 'HealthHeroQuestion')
    OperationLog = apps.get_model('dashboard', 'OperationLog')

    for role in ['owner', 'editor', 'viewer']:
        Group.objects.get_or_create(name=role)

    HomeConfig.objects.update_or_create(
        pk=1,
        defaults={
            'platform_name': 'صيف وصحة - مساعد',
            'tagline': 'مرشدك الصحي في صيف عسير',
            'intro': 'منصة صحية وتوعوية تساعد زائر عسير على إنشاء خطة يومية آمنة، ومعرفة الفعاليات والمواقع القريبة، وجمع أختام جواز صحة عسير.',
            'seasonal_alert': 'نصيحة اليوم: اشرب الماء على دفعات، وخذ استراحة في الظل عند المشي أو حضور الفعاليات.',
            'primary_button_label': 'ابدأ رحلتك الصحية',
            'call937_label': 'اتصال 937',
            'emergency997_label': 'طوارئ 997',
            'hero_image': 'img/asir-hero.png',
            'active': True,
        },
    )

    quick_buttons = [
        ('ابدأ رحلتك الصحية', '/journey/', 'خطة', 1),
        ('اسأل الدكتور مساعد', '/assistant/', 'مساعد', 2),
        ('المواقع القريبة', '/nearby/', 'مواقع', 3),
        ('جواز صحة عسير', '/passport/', 'جواز', 4),
        ('فعاليات اليوم', '/events/', 'فعاليات', 5),
        ('المواد التوعوية', '/downloads/', 'تحميلات', 6),
    ]
    for label, url, icon, order in quick_buttons:
        HomeQuickButton.objects.update_or_create(
            label=label,
            defaults={'url': url, 'icon': icon, 'order': order, 'active': True},
        )

    for key, label in [
        ('health_hero', 'تحدي بطل الصحة'),
        ('passport', 'جواز صحة عسير'),
        ('doctor_assistant', 'الدكتور مساعد'),
        ('qr_tracking', 'تتبع QR'),
    ]:
        FeatureFlag.objects.update_or_create(key=key, defaults={'label': label, 'enabled': True})

    GeneralSettings.objects.update_or_create(
        pk=1,
        defaults={
            'site_name': 'صيف وصحة - مساعد',
            'default_city': 'أبها',
            'support_phone': '937',
            'emergency_phone': '997',
            'achievement_stamp_target': 4,
            'maintenance_mode': False,
            'offline_message': 'يمكنك متابعة الصفحات الأساسية، وسيتم تحديث البيانات عند عودة الاتصال.',
        },
    )

    SmartEntryConfig.objects.update_or_create(
        pk=1,
        defaults={
            'privacy_note': 'نستخدم معرف زائر عشوائي فقط لتحسين الرحلة واحتساب نقاط QR، ولا نجمع رقم الجوال أو موقعا دقيقا.',
            'config': {
                'age_groups': ['أقل من 18', '18 إلى 49', '50 إلى 64', '65 فأكثر'],
                'trip_options': ['سياحة', 'رياضة', 'هايكنج', 'فعاليات عائلية', 'مراكز صحية'],
            },
            'active': True,
        },
    )

    events = [
        ('مسار الضباب الصحي', 'تجربة مشي صباحية بإرشادات ترطيب وقياس نبض قبل الانطلاق.', 'أبها', 'ممشى الضباب - أبها', date(2026, 7, 3), '07:00 ص', 'نشاط بدني', 'العائلات ومحبو النشاط', 'نشاط بدني', 'https://maps.google.com/?q=Abha', True, 1),
        ('نقطة الاطمئنان السريع', 'ركن توعوي في مطار أبها يقدم قياسات أساسية ونصائح سفر صحية.', 'أبها', 'مطار أبها الدولي', date(2026, 7, 4), '04:00 م', 'بوث صحي', 'القادمون إلى عسير', 'توعية وفحص', 'https://maps.google.com/?q=Abha+Airport', True, 2),
        ('الأسرة النشطة في السودة', 'برنامج تفاعلي للأطفال وكبار السن حول السلامة والحركة والغذاء المتوازن.', 'السودة', 'السودة', date(2026, 7, 6), '05:30 م', 'فعالية عائلية', 'الأطفال وكبار السن', 'عائلة', 'https://maps.google.com/?q=Al+Soudah', False, 3),
    ]
    for title, description, city, location, event_date, time, activity_type, audience, category, map_url, show_on_home, order in events:
        HealthEvent.objects.update_or_create(
            title=title,
            defaults={
                'description': description,
                'city': city,
                'location': location,
                'date': event_date,
                'time': time,
                'activity_type': activity_type,
                'audience': audience,
                'category': category,
                'map_url': map_url,
                'show_on_home': show_on_home,
                'order': order,
                'active': True,
            },
        )

    locations = [
        ('مركز صحي وسط أبها', 'health_center', 'أبها', 'قريب من وسط المدينة', '1.8 كم', 'مفتوح حتى 11:00 م', '937', 'https://maps.google.com/?q=Abha+Health+Center', 1),
        ('طوارئ أبها', 'emergency', 'أبها', 'نقطة طوارئ قريبة من وسط المدينة', '2.4 كم', 'مفتوح 24 ساعة', '997', 'https://maps.google.com/?q=Abha+Emergency', 2),
        ('نقطة رعاية السودة الموسمية', 'health_center', 'السودة', 'خدمة صحية موسمية قرب الفعاليات', '3.4 كم', 'مفتوح خلال الفعاليات', '937', 'https://maps.google.com/?q=Al+Soudah+Health', 3),
        ('ممشى الضباب', 'walkway', 'أبها', 'مسار مشي مناسب للصباح والمساء', '900 م', 'مناسب للمشي الخفيف', '', 'https://maps.google.com/?q=Abha+Fog+Walkway', 4),
        ('صيدلية قريبة من المطار', 'pharmacy', 'أبها', 'خدمة أدوية أساسية للقادمين', '1.2 كم', 'حتى منتصف الليل', '937', 'https://maps.google.com/?q=Abha+Pharmacy', 5),
        ('نقطة توعوية عائلية', 'awareness', 'السودة', 'نصائح للأطفال وكبار السن', 'داخل الفعالية', 'خلال البرنامج', '', '/messages/', 6),
    ]
    created_locations = {}
    for name, location_type, city, address, distance_label, availability, phone, map_url, order in locations:
        obj, _ = HealthLocation.objects.update_or_create(
            name=name,
            defaults={
                'location_type': location_type,
                'city': city,
                'address': address,
                'distance_label': distance_label,
                'availability': availability,
                'phone': phone,
                'map_url': map_url,
                'order': order,
                'active': True,
            },
        )
        created_locations[name] = obj

    contents = [
        ('دليل الترطيب في المرتفعات', 'pdf', 'إرشادات عملية لتجنب الجفاف أثناء التنقل والمشي في أجواء عسير.', 'وقاية', 'تنزيل الدليل', '/static/downloads/hydration-guide.pdf', 1),
        ('بطاقة المشي الآمن', 'card', 'خطوات بسيطة قبل وأثناء وبعد المشي للحفاظ على نشاط صحي آمن.', 'نشاط بدني', 'عرض البطاقة', '/static/downloads/walking-card.pdf', 2),
        ('متى أتوجه للطوارئ؟', 'post', 'علامات صحية مهمة أثناء السفر تستدعي طلب المساعدة الفورية.', 'سلامة', 'قراءة المادة', '/static/downloads/emergency-notes.pdf', 3),
    ]
    for title, content_type, summary, category, action_label, file_url, order in contents:
        AwarenessContent.objects.update_or_create(
            title=title,
            defaults={
                'content_type': content_type,
                'summary': summary,
                'category': category,
                'action_label': action_label,
                'file_url': file_url,
                'order': order,
                'active': True,
            },
        )

    messages = [
        ('اشرب الماء قبل العطش', 'خذ رشفات منتظمة خصوصا عند المشي أو انتظار الفعاليات.', 'الترطيب', 'droplet', 1),
        ('وقت المشي الآمن', 'اختر الصباح الباكر أو بعد العصر وتجنب الشمس المباشرة.', 'النشاط البدني', 'sun', 2),
        ('احفظ أرقام المساعدة', '937 للاستشارة الصحية و997 للحالات الإسعافية الطارئة.', 'الطوارئ', 'phone', 3),
        ('راحة كبار السن', 'اختر مسارا قصيرا ومكان جلوس قريبا من الخدمات.', 'كبار السن', 'users', 4),
        ('سلامة الأطفال', 'اتفق مع العائلة على نقطة تجمع واحمل ماء ووجبة خفيفة.', 'الأطفال', 'heart', 5),
    ]
    for title, text, category, icon, order in messages:
        AwarenessMessage.objects.update_or_create(
            title=title,
            defaults={'text': text, 'category': category, 'icon': icon, 'order': order, 'active': True},
        )

    keyword_answers = [
        ('أقرب مركز صحي', ['مركز صحي', 'عيادة', 'مستوصف', 'أقرب مركز', 'رعاية', 'مستشفى'], 'افتح صفحة المواقع القريبة وستجد مراكز صحية وطوارئ وصيدليات مناسبة حسب المدينة.', 'عرض المواقع', '/nearby/'),
        ('الفعاليات الصحية', ['فعالية', 'فعاليات', 'نشاط', 'برنامج', 'حدث'], 'توجد فعاليات صحية وتوعوية في أبها والسودة ومطار أبها، ويمكنك اختيار الأنسب من صفحة الفعاليات.', 'عرض الفعاليات', '/events/'),
        ('الترطيب والإجهاد', ['ماء', 'ترطيب', 'دوخة', 'إجهاد', 'حرارة', 'تعب'], 'اشرب الماء على دفعات، وخذ استراحة في الظل، وتجنب النشاط الشديد وقت الظهيرة.', 'تحميل دليل الترطيب', '/downloads/'),
        ('الطوارئ', ['طوارئ', 'اسعاف', 'ألم صدر', 'اختناق', 'إغماء', 'نزيف'], 'للحالات الطارئة اتصل فورا على 997 أو 937، ولا تنتظر رد المنصة إذا كانت الأعراض شديدة.', 'المواقع القريبة', '/nearby/'),
    ]
    for question, keywords, answer, cta_label, cta_url in keyword_answers:
        KeywordAnswer.objects.update_or_create(
            question=question,
            defaults={'keywords': keywords, 'answer': answer, 'cta_label': cta_label, 'cta_url': cta_url, 'active': True},
        )

    doctor_questions = [
        ('أين أقرب مركز صحي؟', 'استخدم صفحة المواقع القريبة للوصول إلى مركز صحي أو طوارئ حسب احتياجك.', ['مركز صحي', 'أقرب مركز', 'مستشفى', 'عيادة'], 1),
        ('كيف أتواصل مع 937؟', 'اضغط زر الاتصال 937 من أعلى الصفحة أو اتصل مباشرة من هاتفك.', ['937', 'اتصال', 'استشارة'], 2),
        ('ما نصائح الهايكنج؟', 'خذ ماء كافيا، ارتد حذاء مناسبا، استخدم واقي الشمس، ولا تذهب وحدك.', ['هايكنج', 'مسار', 'جبل', 'مشي'], 3),
        ('ما علامات ضربة الشمس؟', 'الدوار والصداع واحمرار الجلد والتعب الشديد علامات تستدعي الراحة وطلب المساعدة.', ['الشمس', 'حرارة', 'دوخة', 'صداع'], 4),
    ]
    for question, answer, keywords, order in doctor_questions:
        DoctorAssistantQuestion.objects.update_or_create(
            question=question,
            defaults={'answer': answer, 'keywords': keywords, 'order': order, 'active': True},
        )

    stamps = [
        ('ختم الترطيب', 'hydration', 'يحصل عليه الزائر عند مسح نقطة توعوية عن الترطيب.', 'droplet', 20),
        ('ختم المشي', 'walking', 'يحصل عليه الزائر عند زيارة ممشى صحي.', 'footprints', 25),
        ('ختم الغذاء الصحي', 'healthy-food', 'يحصل عليه الزائر من نقطة غذاء صحي.', 'utensils', 20),
        ('ختم الوعي', 'awareness', 'يحصل عليه الزائر عند المرور بنقطة توعوية.', 'lightbulb', 15),
        ('ختم الإسعاف', 'first-aid', 'يحصل عليه الزائر عند إكمال محطة الإسعافات الأولية.', 'cross', 30),
    ]
    stamp_map = {}
    for name, slug, description, icon, points in stamps:
        stamp, _ = PassportStamp.objects.update_or_create(
            slug=slug,
            defaults={'name': name, 'description': description, 'icon': icon, 'points': points, 'active': True},
        )
        stamp_map[slug] = stamp

    achievements = [
        ('مستكشف عسير الصحي', 'explorer', 'يفتح عند أول ختم في الجواز.', 'مستكشف الصحة', 15, 1),
        ('سفير الصحة', 'ambassador', 'يفتح عند جمع ثلاثة أختام على الأقل.', 'سفير الصحة', 60, 3),
        ('بطل صيف وصحة', 'summer-hero', 'يفتح عند بلوغ 100 نقطة أو أكثر.', 'بطل صيف وصحة', 100, 4),
    ]
    for name, code, description, badge_label, required_points, required_stamps in achievements:
        PassportAchievement.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'description': description,
                'badge_label': badge_label,
                'required_points': required_points,
                'required_stamps': required_stamps,
                'active': True,
            },
        )

    qr_locations = [
        ('بوابة السودة الصحية', 'soudah-gate', 'تسجيل زيارة موقع السودة ونقطة الرعاية الموسمية.', 'موقع', 'السودة', '/nearby/', created_locations.get('نقطة رعاية السودة الموسمية')),
        ('ممشى الضباب', 'fog-walkway', 'تسجيل زيارة ممشى الضباب الصحي.', 'ممشى', 'أبها', '/events/', created_locations.get('ممشى الضباب')),
        ('نقطة مطار أبها', 'abha-airport', 'تسجيل زيارة نقطة الاطمئنان السريع في المطار.', 'بوث صحي', 'أبها', '/events/', None),
    ]
    for name, slug, description, category, city, target_url, related_location in qr_locations:
        QrLocation.objects.update_or_create(
            slug=slug,
            defaults={
                'name': name,
                'description': description,
                'category': category,
                'city': city,
                'target_url': target_url,
                'related_location': related_location,
                'active': True,
            },
        )

    qr_items = [
        ('نقطة الترطيب', 'توعية', 'امسح للحصول على ختم الترطيب.', '/downloads/', stamp_map.get('hydration')),
        ('تحدي ممشى الضباب', 'نشاط', 'امسح بعد زيارة الممشى للحصول على ختم المشي.', '/passport/', stamp_map.get('walking')),
        ('محطة الإسعافات الأولية', 'توعية', 'امسح بعد إكمال محطة الإسعاف.', '/messages/', stamp_map.get('first-aid')),
        ('ركن الوعي العائلي', 'توعية', 'امسح للحصول على ختم الوعي.', '/messages/', stamp_map.get('awareness')),
    ]
    for title, item_type, description, target_url, stamp in qr_items:
        QrItem.objects.update_or_create(
            title=title,
            defaults={
                'item_type': item_type,
                'description': description,
                'target_url': target_url,
                'stamp': stamp,
                'active': True,
            },
        )

    hero_questions = [
        ('كم مرة ينبغي شرب الماء خلال رحلة مشي في عسير؟', ['مرة واحدة قبل المشي', 'كل 20 إلى 30 دقيقة', 'فقط عند الشعور بالعطش'], 1, 'إجابة ممتازة في الترطيب.', 'الترطيب المنتظم يحمي جسمك من الإجهاد.'),
        ('ما أفضل وقت للمشي والنشاط؟', ['وقت الظهيرة تحت الشمس', 'الصباح الباكر أو بعد العصر', 'أي وقت دون قيود'], 1, 'اختيار آمن للنشاط.', 'الصباح والمساء أوقات مناسبة لتجنب الحرارة.'),
        ('ما علامة التحذير من ضربة الشمس؟', ['الشعور بالجوع', 'الدوار والصداع واحمرار الجلد', 'الشعور بالبرد فقط'], 1, 'تعرفك على علامات الخطر مهم.', 'عند هذه الأعراض انتقل للظل واطلب المساعدة.'),
    ]
    for order, (question, options, correct_index, result_message, tip) in enumerate(hero_questions, start=1):
        HealthHeroQuestion.objects.update_or_create(
            question=question,
            defaults={
                'options': options,
                'correct_index': correct_index,
                'result_message': result_message,
                'tip': tip,
                'order': order,
                'active': True,
            },
        )

    OperationLog.objects.get_or_create(
        action='تهيئة البيانات',
        detail='تم إنشاء بيانات البداية الافتراضية لمنصة صيف وصحة - مساعد.',
    )


def reverse_seed_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('core', '0001_initial'),
        ('events', '0001_initial'),
        ('locations', '0001_initial'),
        ('awareness', '0001_initial'),
        ('assistant', '0001_initial'),
        ('passport', '0001_initial'),
        ('qr', '0001_initial'),
        ('hero', '0001_initial'),
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_seed_data),
    ]
