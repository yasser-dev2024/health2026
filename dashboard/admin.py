from django.contrib import admin

from .models import OperationLog


@admin.register(OperationLog)
class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'ip_address', 'created_at')
    search_fields = ('action', 'detail', 'user__username')
    list_filter = ('created_at',)

# Register your models here.
