from django.contrib import admin

from .models import (
    FeatureFlag,
    GeneralSettings,
    HomeConfig,
    HomeQuickButton,
    SmartEntryConfig,
)


@admin.register(HomeConfig)
class HomeConfigAdmin(admin.ModelAdmin):
    list_display = ('platform_name', 'tagline', 'active', 'updated_at')


@admin.register(HomeQuickButton)
class HomeQuickButtonAdmin(admin.ModelAdmin):
    list_display = ('label', 'url', 'order', 'active')
    list_editable = ('order', 'active')


@admin.register(FeatureFlag)
class FeatureFlagAdmin(admin.ModelAdmin):
    list_display = ('label', 'key', 'enabled')
    list_editable = ('enabled',)


@admin.register(GeneralSettings)
class GeneralSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'default_city', 'support_phone', 'emergency_phone')
    fieldsets = (
        ('الإعدادات العامة', {
            'fields': (
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
class SmartEntryConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'active', 'updated_at')

# Register your models here.
