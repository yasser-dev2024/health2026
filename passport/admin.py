from django.contrib import admin

from campaigns.admin_mixins import ActiveCampaignAdminMixin

from .models import PassportAchievement, PassportStamp, VisitorPassport


@admin.register(PassportStamp)
class PassportStampAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'campaign', 'slug', 'points', 'active')
    list_filter = ('campaign', 'active')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PassportAchievement)
class PassportAchievementAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'campaign', 'code', 'required_points', 'required_stamps', 'active')
    list_filter = ('campaign', 'active')
    prepopulated_fields = {'code': ('name',)}


@admin.register(VisitorPassport)
class VisitorPassportAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('visitor_id', 'campaign', 'points', 'scans_count', 'updated_at')
    list_filter = ('campaign',)
    search_fields = ('visitor_id',)
    filter_horizontal = ('stamps', 'achievements')

# Register your models here.
