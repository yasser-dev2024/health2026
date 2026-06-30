from django.contrib import admin

from campaigns.admin_mixins import ActiveCampaignAdminMixin

from .models import HealthLocation


@admin.register(HealthLocation)
class HealthLocationAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'campaign', 'location_type', 'city', 'availability', 'active')
    list_filter = ('campaign', 'active', 'location_type', 'city')
    search_fields = ('name', 'address', 'city')
    list_editable = ('active',)

# Register your models here.
