from django.db import models


class PassportStamp(models.Model):
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='passport_stamps',
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=80, db_index=True)
    description = models.TextField()
    icon = models.CharField(max_length=40, blank=True)
    points = models.PositiveIntegerField(default=20)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ('campaign', 'slug')
        verbose_name = 'ختم جواز'
        verbose_name_plural = 'أختام الجواز'

    def __str__(self):
        return self.name


class PassportAchievement(models.Model):
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='passport_achievements',
    )
    name = models.CharField(max_length=120)
    code = models.SlugField(max_length=80, db_index=True)
    description = models.TextField()
    badge_label = models.CharField(max_length=80)
    required_points = models.PositiveIntegerField(default=0)
    required_stamps = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['required_points', 'required_stamps', 'name']
        unique_together = ('campaign', 'code')
        verbose_name = 'إنجاز جواز'
        verbose_name_plural = 'إنجازات الجواز'

    def __str__(self):
        return self.name


class VisitorPassport(models.Model):
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='visitor_passports',
    )
    visitor_id = models.CharField(max_length=64, db_index=True)
    points = models.PositiveIntegerField(default=0)
    scans_count = models.PositiveIntegerField(default=0)
    stamps = models.ManyToManyField(PassportStamp, blank=True, related_name='passports')
    achievements = models.ManyToManyField(PassportAchievement, blank=True, related_name='passports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('campaign', 'visitor_id')
        verbose_name = 'جواز زائر'
        verbose_name_plural = 'جوازات الزوار'

    def __str__(self):
        return self.visitor_id

    @property
    def stamp_count(self):
        return self.stamps.count()

# Create your models here.
