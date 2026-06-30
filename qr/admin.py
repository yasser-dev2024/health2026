from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import QrItem, QrLocation, QrLocationVisit, QrScan, QrVisit, QrVisitorProfile


@admin.register(QrLocation)
class QrLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'city', 'category', 'scans_count', 'last_scan_at', 'active', 'download_qr')
    list_filter = ('active', 'city', 'category')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('scans_count', 'last_scan_at', 'download_qr')

    def download_qr(self, obj):
        if not obj.pk:
            return '-'
        url = f"{reverse('admin_qr_location_png', kwargs={'location_id': obj.pk})}?download=1"
        return format_html('<a href="{}">تنزيل QR للطباعة</a>', url)

    download_qr.short_description = 'QR'


@admin.register(QrItem)
class QrItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'item_type', 'stamp', 'scans_count', 'active')
    list_filter = ('active', 'item_type')
    search_fields = ('title', 'description')


@admin.register(QrScan)
class QrScanAdmin(admin.ModelAdmin):
    list_display = ('visitor_id', 'qr_type', 'path', 'created_at')
    list_filter = ('qr_type', 'created_at')
    search_fields = ('visitor_id', 'path')


@admin.register(QrVisit)
class QrVisitAdmin(admin.ModelAdmin):
    list_display = ('visitor_id', 'qr_item', 'created_at')
    search_fields = ('visitor_id', 'qr_item__title')


@admin.register(QrLocationVisit)
class QrLocationVisitAdmin(admin.ModelAdmin):
    list_display = ('visitor_id', 'qr_location', 'created_at')
    search_fields = ('visitor_id', 'qr_location__name')


@admin.register(QrVisitorProfile)
class QrVisitorProfileAdmin(admin.ModelAdmin):
    list_display = ('visitor_id', 'qr_location', 'visitor_type', 'party_type', 'age_group', 'health_topic', 'updated_at')
    list_filter = ('visitor_type', 'party_type', 'age_group', 'health_topic', 'qr_location')
    search_fields = ('visitor_id', 'qr_location__name')
    readonly_fields = ('visitor_id', 'created_at', 'updated_at')

# Register your models here.
