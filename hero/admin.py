from django.contrib import admin

from campaigns.admin_mixins import ActiveCampaignAdminMixin

from .models import HealthHeroEntry, HealthHeroQuestion


@admin.register(HealthHeroQuestion)
class HealthHeroQuestionAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('question', 'campaign', 'order', 'active')
    list_filter = ('campaign', 'active')
    list_editable = ('order', 'active')
    search_fields = ('question',)


@admin.register(HealthHeroEntry)
class HealthHeroEntryAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('participant_name', 'campaign', 'phone', 'score', 'total', 'badge_label', 'created_at')
    list_filter = ('campaign', 'badge_label', 'created_at')
    search_fields = ('visitor_id', 'participant_name', 'phone', 'badge_label')
    readonly_fields = ('visitor_id', 'score', 'total', 'badge_label', 'answers', 'created_at')

# Register your models here.
