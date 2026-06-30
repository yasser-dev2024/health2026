from django.contrib import admin

from .models import HealthEvent


@admin.register(HealthEvent)
class HealthEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'date', 'time', 'category', 'active', 'show_on_home')
    list_filter = ('active', 'show_on_home', 'city', 'category')
    search_fields = ('title', 'description', 'location')
    list_editable = ('active', 'show_on_home')

# Register your models here.
