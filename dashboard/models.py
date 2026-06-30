from django.conf import settings
from django.db import models


class OperationLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=120)
    detail = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'سجل عملية'
        verbose_name_plural = 'سجل العمليات الإدارية'

    def __str__(self):
        return self.action

# Create your models here.
