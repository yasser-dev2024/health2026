from django.contrib import admin

from .models import HealthLocation


@admin.register(HealthLocation)
class HealthLocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'location_type', 'city', 'availability', 'active')
    list_filter = ('active', 'location_type', 'city')
    search_fields = ('name', 'address', 'city')
    list_editable = ('active',)

# Register your models here.
