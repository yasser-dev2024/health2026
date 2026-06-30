from django.contrib import admin

from campaigns.admin_mixins import ActiveCampaignAdminMixin

from .models import HealthEvent


@admin.register(HealthEvent)
class HealthEventAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'campaign', 'city', 'date', 'time', 'category', 'active', 'show_on_home')
    list_filter = ('campaign', 'active', 'show_on_home', 'city', 'category')
    search_fields = ('title', 'description', 'location')
    list_editable = ('active', 'show_on_home')

# Register your models here.
