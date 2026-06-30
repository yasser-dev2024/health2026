from django.contrib import admin

from .models import AwarenessContent, AwarenessMessage


@admin.register(AwarenessContent)
class AwarenessContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_type', 'category', 'download_count', 'active', 'updated_at')
    list_filter = ('active', 'content_type', 'category')
    search_fields = ('title', 'summary')
    list_editable = ('active',)
    readonly_fields = ('download_count', 'created_at', 'updated_at')
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('title', 'content_type', 'category', 'summary', 'action_label', 'order', 'active'),
        }),
        ('الملف — ارفع من الجهاز أو أدخل رابط خارجي', {
            'description': 'استخدم "رفع ملف من الجهاز" لرفع الملف مباشرة، أو أدخل رابطاً خارجياً في حقل "رابط الملف".',
            'fields': ('file_upload', 'file_url'),
        }),
        ('الصورة المصغرة — ارفع من الجهاز أو أدخل رابط', {
            'description': 'استخدم "رفع صورة مصغرة" لرفع الصورة مباشرة، أو أدخل رابطاً خارجياً.',
            'fields': ('thumbnail_upload', 'thumbnail_url'),
        }),
        ('الإحصائيات', {
            'fields': ('download_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(AwarenessMessage)
class AwarenessMessageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'order', 'active')
    list_filter = ('active', 'category')
    search_fields = ('title', 'text')
    list_editable = ('order', 'active')
