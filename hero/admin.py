from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

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
    list_display = ('participant_name', 'campaign', 'phone', 'score', 'total', 'badge_label', 'certificate_link', 'created_at')
    list_filter = ('campaign', 'badge_label', 'created_at')
    search_fields = ('visitor_id', 'participant_name', 'phone', 'badge_label')
    readonly_fields = ('visitor_id', 'score', 'total', 'badge_label', 'answers', 'certificate_link', 'created_at')

    @admin.display(description='الشهادة')
    def certificate_link(self, obj):
        if not obj.pk:
            return '-'
        url = reverse('hero_certificate', args=[obj.pk])
        return format_html('<a class="button" href="{}" target="_blank">عرض الشهادة</a>', url)

# Register your models here.
