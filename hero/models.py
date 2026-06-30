from django.db import models


class HealthHeroQuestion(models.Model):
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='hero_questions',
    )
    question = models.CharField(max_length=240)
    options = models.JSONField(default=list)
    correct_index = models.PositiveIntegerField(default=0)
    result_message = models.CharField(max_length=180)
    tip = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'سؤال تحدي بطل الصحة'
        verbose_name_plural = 'أسئلة تحدي بطل الصحة'

    def __str__(self):
        return self.question


class HealthHeroEntry(models.Model):
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='hero_entries',
    )
    visitor_id = models.CharField(max_length=64, db_index=True)
    participant_name = models.CharField(max_length=120, blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    score = models.PositiveIntegerField(default=0)
    total = models.PositiveIntegerField(default=0)
    badge_label = models.CharField(max_length=120)
    answers = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'مشاركة تحدي'
        verbose_name_plural = 'المشاركون في تحدي بطل الصحة'

    def __str__(self):
        name = self.participant_name or self.visitor_id
        return f'{name} - {self.score}/{self.total}'

# Create your models here.
