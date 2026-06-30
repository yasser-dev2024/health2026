from django.db import models

from core.validators import validate_safe_url


class HealthLocation(models.Model):
    TYPE_HEALTH_CENTER = 'health_center'
    TYPE_HOSPITAL = 'hospital'
    TYPE_PHARMACY = 'pharmacy'
    TYPE_WALKWAY = 'walkway'
    TYPE_AWARENESS = 'awareness'
    TYPE_EMERGENCY = 'emergency'
    TYPE_CHOICES = [
        (TYPE_HEALTH_CENTER, 'مركز صحي'),
        (TYPE_HOSPITAL, 'مستشفى'),
        (TYPE_PHARMACY, 'صيدلية'),
        (TYPE_WALKWAY, 'ممشى'),
        (TYPE_AWARENESS, 'نقطة توعوية'),
        (TYPE_EMERGENCY, 'طوارئ'),
    ]

    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='health_locations',
    )
    name = models.CharField(max_length=160)
    location_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=TYPE_HEALTH_CENTER)
    city = models.CharField(max_length=80, default='أبها')
    address = models.CharField(max_length=220, blank=True)
    distance_label = models.CharField(max_length=60, blank=True)
    availability = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    map_url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'city', 'name']
        verbose_name = 'موقع صحي ومهم'
        verbose_name_plural = 'المواقع الصحية والمهمة'

    def __str__(self):
        return self.name

# Create your models here.
