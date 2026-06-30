from django.contrib import admin

from campaigns.admin_mixins import ActiveCampaignAdminMixin

from .models import OperationLog


@admin.register(OperationLog)
class OperationLogAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('action', 'campaign', 'user', 'ip_address', 'created_at')
    search_fields = ('action', 'detail', 'user__username')
    list_filter = ('campaign', 'created_at')

# Register your models here.
