from django.contrib import admin

from .models import PassportAchievement, PassportStamp, VisitorPassport


@admin.register(PassportStamp)
class PassportStampAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'points', 'active')
    list_filter = ('active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PassportAchievement)
class PassportAchievementAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'required_points', 'required_stamps', 'active')
    list_filter = ('active',)
    prepopulated_fields = {'code': ('name',)}


@admin.register(VisitorPassport)
class VisitorPassportAdmin(admin.ModelAdmin):
    list_display = ('visitor_id', 'points', 'scans_count', 'updated_at')
    search_fields = ('visitor_id',)
    filter_horizontal = ('stamps', 'achievements')

# Register your models here.
