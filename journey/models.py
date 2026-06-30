from django.db import models


class JourneySubmission(models.Model):
    visitor_id = models.CharField(max_length=64, db_index=True)
    current_location = models.CharField(max_length=80)
    age_group = models.CharField(max_length=30)
    party_type = models.CharField(max_length=30)
    visit_purpose = models.CharField(max_length=40)
    has_health_condition = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'إجابة رحلة'
        verbose_name_plural = 'إجابات الرحلات'

    def __str__(self):
        return f'{self.visitor_id} - {self.created_at:%Y-%m-%d}'

# Create your models here.
