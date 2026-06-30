from django.contrib import admin

from .models import HealthHeroEntry, HealthHeroQuestion


@admin.register(HealthHeroQuestion)
class HealthHeroQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'active')
    list_filter = ('active',)
    list_editable = ('order', 'active')
    search_fields = ('question',)


@admin.register(HealthHeroEntry)
class HealthHeroEntryAdmin(admin.ModelAdmin):
    list_display = ('participant_name', 'phone', 'score', 'total', 'badge_label', 'created_at')
    list_filter = ('badge_label', 'created_at')
    search_fields = ('visitor_id', 'participant_name', 'phone', 'badge_label')
    readonly_fields = ('visitor_id', 'score', 'total', 'badge_label', 'answers', 'created_at')

# Register your models here.
