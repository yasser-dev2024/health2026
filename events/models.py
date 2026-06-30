from django.db import models

from core.validators import validate_safe_url


class HealthEvent(models.Model):
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='health_events',
    )
    title = models.CharField(max_length=160)
    description = models.TextField()
    city = models.CharField(max_length=80, default='أبها')
    location = models.CharField(max_length=160)
    date = models.DateField()
    time = models.CharField(max_length=40)
    activity_type = models.CharField(max_length=90, blank=True)
    audience = models.CharField(max_length=140, blank=True)
    category = models.CharField(max_length=90, default='توعية')
    map_url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    show_on_home = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    visits = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'date', 'time']
        verbose_name = 'فعالية صحية'
        verbose_name_plural = 'الفعاليات الصحية'

    def __str__(self):
        return self.title

# Create your models here.
