from django.db import models

from core.validators import validate_safe_url


class KeywordAnswer(models.Model):
    question = models.CharField(max_length=180)
    keywords = models.JSONField(default=list)
    answer = models.TextField()
    link_label = models.CharField(max_length=80, blank=True)
    link_url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['question']
        verbose_name = 'كلمة مفتاحية وإجابة'
        verbose_name_plural = 'الكلمات المفتاحية والإجابات'

    def __str__(self):
        return self.question


class DoctorAssistantQuestion(models.Model):
    question = models.CharField(max_length=180)
    answer = models.TextField()
    keywords = models.JSONField(default=list)
    link_label = models.CharField(max_length=80, blank=True)
    link_url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    usage_count = models.PositiveIntegerField(default=0)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'question']
        verbose_name = 'سؤال الدكتور مساعد'
        verbose_name_plural = 'أسئلة الدكتور مساعد'

    def __str__(self):
        return self.question

# Create your models here.
