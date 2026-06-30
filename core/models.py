from django.db import models

from .validators import validate_safe_url


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class HomeConfig(TimeStampedModel):
    platform_name = models.CharField(max_length=120, default='صيف وصحة - مساعد')
    tagline = models.CharField(max_length=180, default='مرشدك الصحي في صيف عسير')
    intro = models.TextField(
        default='منصة صحية وتوعوية تساعد زائر عسير على اختيار خطة آمنة وموقع مناسب ومحتوى صحي موثوق.'
    )
    seasonal_alert = models.CharField(
        max_length=240,
        default='اشرب الماء على دفعات، وخذ استراحة في الظل عند المشي أو حضور الفعاليات.',
    )
    primary_button_label = models.CharField(max_length=80, default='ابدأ رحلتك الصحية')
    call937_label = models.CharField(max_length=80, default='اتصال 937')
    emergency997_label = models.CharField(max_length=80, default='طوارئ 997')
    hero_image = models.CharField(max_length=200, blank=True, default='img/asir-hero.png')
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'إعداد الصفحة الرئيسية'
        verbose_name_plural = 'إعدادات الصفحة الرئيسية'

    def __str__(self):
        return self.platform_name


class HomeQuickButton(TimeStampedModel):
    label = models.CharField(max_length=90)
    url = models.CharField(max_length=220, validators=[validate_safe_url])
    icon = models.CharField(max_length=40, blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'زر سريع'
        verbose_name_plural = 'الأزرار السريعة'

    def __str__(self):
        return self.label


class FeatureFlag(TimeStampedModel):
    key = models.SlugField(max_length=80, unique=True)
    label = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ['label']
        verbose_name = 'ميزة'
        verbose_name_plural = 'تفعيل وتعطيل الميزات'

    def __str__(self):
        return self.label


class GeneralSettings(TimeStampedModel):
    site_name = models.CharField(max_length=120, default='صيف وصحة - مساعد')
    default_city = models.CharField(max_length=80, default='أبها')
    support_phone = models.CharField(max_length=30, default='937')
    emergency_phone = models.CharField(max_length=30, default='997')
    achievement_stamp_target = models.PositiveIntegerField(default=4)
    maintenance_mode = models.BooleanField(default=False)
    offline_message = models.TextField(
        default='يمكنك متابعة تصفح الصفحات الأساسية، وسيتم تحديث البيانات عند عودة الاتصال.'
    )
    restaurants_map_url = models.CharField('رابط المطاعم في خريطة عسير', max_length=240, validators=[validate_safe_url], blank=True)
    hotels_map_url = models.CharField('رابط الفنادق في خريطة عسير', max_length=240, validators=[validate_safe_url], blank=True)
    events_map_url = models.CharField('رابط الفعاليات في خريطة عسير', max_length=240, validators=[validate_safe_url], blank=True)
    hiking_map_url = models.CharField('رابط الهايكنج في خريطة عسير', max_length=240, validators=[validate_safe_url], blank=True)
    landmarks_map_url = models.CharField('رابط المعالم في خريطة عسير', max_length=240, validators=[validate_safe_url], blank=True)
    parks_map_url = models.CharField('رابط الحدائق في خريطة عسير', max_length=240, validators=[validate_safe_url], blank=True)

    class Meta:
        verbose_name = 'إعداد عام'
        verbose_name_plural = 'الإعدادات العامة'

    def __str__(self):
        return self.site_name


class SmartEntryConfig(TimeStampedModel):
    privacy_note = models.TextField(
        default='نستخدم معرف زائر عشوائي فقط لتحسين الرحلة واحتساب نقاط QR، ولا نجمع رقم الجوال أو موقعا دقيقا.'
    )
    config = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'إعداد الدخول الذكي'
        verbose_name_plural = 'إعدادات الدخول الذكي'

    def __str__(self):
        return 'إعداد الدخول الذكي'

# Create your models here.
