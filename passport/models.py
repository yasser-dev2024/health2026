from django.db import models


class PassportStamp(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=80, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=40, blank=True)
    points = models.PositiveIntegerField(default=20)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'ختم جواز'
        verbose_name_plural = 'أختام الجواز'

    def __str__(self):
        return self.name


class PassportAchievement(models.Model):
    name = models.CharField(max_length=120)
    code = models.SlugField(max_length=80, unique=True)
    description = models.TextField()
    badge_label = models.CharField(max_length=80)
    required_points = models.PositiveIntegerField(default=0)
    required_stamps = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['required_points', 'required_stamps', 'name']
        verbose_name = 'إنجاز جواز'
        verbose_name_plural = 'إنجازات الجواز'

    def __str__(self):
        return self.name


class VisitorPassport(models.Model):
    visitor_id = models.CharField(max_length=64, unique=True)
    points = models.PositiveIntegerField(default=0)
    scans_count = models.PositiveIntegerField(default=0)
    stamps = models.ManyToManyField(PassportStamp, blank=True, related_name='passports')
    achievements = models.ManyToManyField(PassportAchievement, blank=True, related_name='passports')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'جواز زائر'
        verbose_name_plural = 'جوازات الزوار'

    def __str__(self):
        return self.visitor_id

    @property
    def stamp_count(self):
        return self.stamps.count()

# Create your models here.
