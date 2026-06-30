from django.contrib import admin

from .models import JourneySubmission


@admin.register(JourneySubmission)
class JourneySubmissionAdmin(admin.ModelAdmin):
    list_display = ('visitor_id', 'current_location', 'age_group', 'party_type', 'visit_purpose', 'has_health_condition', 'created_at')
    list_filter = ('age_group', 'party_type', 'visit_purpose', 'has_health_condition')
    search_fields = ('visitor_id', 'current_location')

# Register your models here.
