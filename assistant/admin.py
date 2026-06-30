from django.contrib import admin

from .models import DoctorAssistantQuestion, KeywordAnswer


@admin.register(KeywordAnswer)
class KeywordAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'active', 'usage_count', 'last_used_at')
    list_filter = ('active',)
    search_fields = ('question', 'answer')
    list_editable = ('active',)


@admin.register(DoctorAssistantQuestion)
class DoctorAssistantQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'active', 'usage_count')
    list_filter = ('active',)
    search_fields = ('question', 'answer', 'keywords')
    list_editable = ('order', 'active')
    fieldsets = (
        (None, {'fields': ('question', 'answer', 'keywords')}),
        ('الأزرار والروابط', {'fields': ('cta_label', 'cta_url', 'link_label', 'link_url')}),
        ('النشر والإحصائيات', {'fields': ('active', 'order', 'usage_count', 'last_used_at')}),
    )
    readonly_fields = ('usage_count', 'last_used_at')

# Register your models here.
