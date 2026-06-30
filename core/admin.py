from django.contrib import admin

from campaigns.admin_mixins import ActiveCampaignAdminMixin

from .models import (
    FeatureFlag,
    GeneralSettings,
    HomeConfig,
    HomeQuickButton,
    SmartEntryConfig,
)


@admin.register(HomeConfig)
class HomeConfigAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('platform_name', 'campaign', 'tagline', 'active', 'updated_at')
    list_filter = ('campaign', 'active')


@admin.register(HomeQuickButton)
class HomeQuickButtonAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('label', 'campaign', 'url', 'order', 'active')
    list_filter = ('campaign', 'active')
    list_editable = ('order', 'active')


@admin.register(FeatureFlag)
class FeatureFlagAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('label', 'campaign', 'key', 'enabled')
    list_filter = ('campaign', 'enabled')
    list_editable = ('enabled',)


@admin.register(GeneralSettings)
class GeneralSettingsAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('site_name', 'campaign', 'default_city', 'support_phone', 'emergency_phone')
    list_filter = ('campaign', 'maintenance_mode')
    fieldsets = (
        ('الإعدادات العامة', {
            'fields': (
                'campaign',
                'site_name',
                'default_city',
                'support_phone',
                'emergency_phone',
                'achievement_stamp_target',
                'maintenance_mode',
                'offline_message',
            )
        }),
        ('روابط خريطة عسير', {
            'fields': (
                'restaurants_map_url',
                'hotels_map_url',
                'events_map_url',
                'hiking_map_url',
                'landmarks_map_url',
                'parks_map_url',
            )
        }),
    )


@admin.register(SmartEntryConfig)
class SmartEntryConfigAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'campaign', 'active', 'updated_at')
    list_filter = ('campaign', 'active')

# Register your models here.
