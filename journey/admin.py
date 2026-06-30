from django.contrib import admin

from campaigns.admin_mixins import ActiveCampaignAdminMixin

from .models import JourneySubmission


@admin.register(JourneySubmission)
class JourneySubmissionAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('visitor_id', 'campaign', 'current_location', 'age_group', 'party_type', 'visit_purpose', 'has_health_condition', 'created_at')
    list_filter = ('campaign', 'age_group', 'party_type', 'visit_purpose', 'has_health_condition')
    search_fields = ('visitor_id', 'current_location')

# Register your models here.
