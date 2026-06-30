from django.db import models

from core.validators import validate_safe_url


class QrLocation(models.Model):
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='qr_locations',
    )
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=90, db_index=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=80, default='موقع')
    city = models.CharField(max_length=80, default='أبها')
    target_url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    related_location = models.ForeignKey(
        'locations.HealthLocation',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='qr_locations',
    )
    scans_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    last_scan_at = models.DateTimeField('آخر مسح', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['city', 'name']
        unique_together = ('campaign', 'slug')
        verbose_name = 'موقع QR'
        verbose_name_plural = 'مواقع QR'

    def __str__(self):
        return self.name


class QrItem(models.Model):
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='qr_items',
    )
    title = models.CharField(max_length=140)
    item_type = models.CharField(max_length=80, default='عنصر')
    description = models.TextField(blank=True)
    target_url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    stamp = models.ForeignKey(
        'passport.PassportStamp',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='qr_items',
    )
    scans_count = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        verbose_name = 'عنصر QR'
        verbose_name_plural = 'عناصر QR'

    def __str__(self):
        return self.title


class QrScan(models.Model):
    TYPE_LOCATION = 'location'
    TYPE_ITEM = 'item'
    TYPE_CHOICES = [
        (TYPE_LOCATION, 'موقع'),
        (TYPE_ITEM, 'عنصر'),
    ]

    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='qr_scans',
    )
    visitor_id = models.CharField(max_length=64, db_index=True)
    qr_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    path = models.CharField(max_length=240)
    qr_location = models.ForeignKey(QrLocation, null=True, blank=True, on_delete=models.SET_NULL)
    qr_item = models.ForeignKey(QrItem, null=True, blank=True, on_delete=models.SET_NULL)
    user_agent = models.CharField(max_length=260, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'مسح QR'
        verbose_name_plural = 'مسوحات QR'

    def __str__(self):
        return f'{self.qr_type} - {self.visitor_id}'


class QrVisit(models.Model):
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='qr_item_visits',
    )
    visitor_id = models.CharField(max_length=64, db_index=True)
    qr_item = models.ForeignKey(QrItem, on_delete=models.CASCADE, related_name='visits')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'زيارة عنصر QR'
        verbose_name_plural = 'زيارات عناصر QR'

    def __str__(self):
        return f'{self.qr_item} - {self.visitor_id}'


class QrLocationVisit(models.Model):
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='qr_location_visits',
    )
    visitor_id = models.CharField(max_length=64, db_index=True)
    qr_location = models.ForeignKey(QrLocation, on_delete=models.CASCADE, related_name='visits')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'زيارة موقع QR'
        verbose_name_plural = 'زيارات مواقع QR'

    def __str__(self):
        return f'{self.qr_location} - {self.visitor_id}'


class QrVisitorProfile(models.Model):
    VISITOR = 'visitor'
    RESIDENT = 'resident'
    VISITOR_TYPE_CHOICES = [
        (VISITOR, 'زائر'),
        (RESIDENT, 'مقيم'),
    ]

    INDIVIDUAL = 'individual'
    FAMILY = 'family'
    PARTY_TYPE_CHOICES = [
        (INDIVIDUAL, 'فرد'),
        (FAMILY, 'عائلة'),
    ]

    UNDER_18 = 'under_18'
    AGE_18_30 = '18_30'
    AGE_31_50 = '31_50'
    AGE_51_PLUS = '51_plus'
    AGE_GROUP_CHOICES = [
        (UNDER_18, 'أقل من 18'),
        (AGE_18_30, '18-30'),
        (AGE_31_50, '31-50'),
        (AGE_51_PLUS, '51+'),
    ]

    BLOOD_PRESSURE = 'blood_pressure'
    DIABETES = 'diabetes'
    HEART_HEALTH = 'heart_health'
    NUTRITION = 'nutrition'
    PHYSICAL_ACTIVITY = 'physical_activity'
    WALKING = 'walking'
    ELDERLY = 'elderly'
    SLEEP = 'sleep'
    SUN_PROTECTION = 'sun_protection'
    HEALTH_TOPIC_CHOICES = [
        (BLOOD_PRESSURE, 'ضغط الدم'),
        (DIABETES, 'السكري'),
        (HEART_HEALTH, 'صحة القلب'),
        (NUTRITION, 'التغذية'),
        (PHYSICAL_ACTIVITY, 'النشاط البدني'),
        (WALKING, 'المشي'),
        (ELDERLY, 'كبار السن'),
        (SLEEP, 'النوم'),
        (SUN_PROTECTION, 'الوقاية من الشمس'),
    ]

    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='qr_visitor_profiles',
    )
    visitor_id = models.CharField(max_length=64, db_index=True)
    qr_location = models.ForeignKey(
        QrLocation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='visitor_profiles',
    )
    visitor_type = models.CharField(max_length=20, choices=VISITOR_TYPE_CHOICES, blank=True)
    party_type = models.CharField(max_length=20, choices=PARTY_TYPE_CHOICES, blank=True)
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES, blank=True)
    health_topic = models.CharField(max_length=40, choices=HEALTH_TOPIC_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('campaign', 'visitor_id')
        verbose_name = 'إحصائية زائر QR'
        verbose_name_plural = 'إحصائيات زوار QR'

    def __str__(self):
        return self.visitor_id

# Create your models here.
