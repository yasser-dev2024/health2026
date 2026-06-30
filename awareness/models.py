from django.db import models

from core.validators import validate_safe_url


class AwarenessContent(models.Model):
    TYPE_PDF = 'pdf'
    TYPE_CARD = 'card'
    TYPE_POST = 'post'
    TYPE_LINK = 'link'
    TYPE_CHOICES = [
        (TYPE_PDF, 'PDF'),
        (TYPE_CARD, 'بطاقة'),
        (TYPE_POST, 'مقال'),
        (TYPE_LINK, 'رابط'),
    ]

    title = models.CharField(max_length=160)
    content_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_PDF)
    summary = models.TextField()
    category = models.CharField(max_length=80, default='توعية')
    action_label = models.CharField(max_length=80, default='عرض')
    file_url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    thumbnail_url = models.CharField(max_length=240, validators=[validate_safe_url], blank=True)
    file_upload = models.FileField(upload_to='awareness/files/', blank=True, null=True, verbose_name='رفع ملف من الجهاز')
    thumbnail_upload = models.ImageField(upload_to='awareness/thumbnails/', blank=True, null=True, verbose_name='رفع صورة مصغرة')
    download_count = models.PositiveIntegerField(default=0)

    def get_file_src(self):
        if self.file_upload:
            return self.file_upload.url
        return self.file_url

    def get_thumbnail_src(self):
        if self.thumbnail_upload:
            return self.thumbnail_upload.url
        return self.thumbnail_url
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    updated_at = models.DateField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'محتوى تحميل'
        verbose_name_plural = 'مكتبة التحميلات'

    def __str__(self):
        return self.title


class AwarenessMessage(models.Model):
    title = models.CharField(max_length=140)
    text = models.TextField()
    category = models.CharField(max_length=80, default='نصيحة')
    icon = models.CharField(max_length=40, blank=True)
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'رسالة توعوية'
        verbose_name_plural = 'الرسائل التوعوية'

    def __str__(self):
        return self.title

# Create your models here.
