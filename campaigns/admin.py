from django.contrib import admin, messages
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.html import format_html

from .admin_mixins import ActiveCampaignAdminMixin
from qr.services import build_qr_location_url, generate_qr_png
from qr.models import QrLocation

from .models import Campaign, CampaignButton, CampaignInteraction, CampaignPage
from .services import campaign_stats, get_active_campaign


class CampaignButtonInline(ActiveCampaignAdminMixin, admin.TabularInline):
    model = CampaignButton
    fk_name = 'page'
    extra = 1
    fields = ('label', 'icon', 'color', 'order', 'action_type', 'target_page', 'url', 'deep_link', 'active')


class CampaignPageInline(ActiveCampaignAdminMixin, admin.StackedInline):
    model = CampaignPage
    extra = 0
    fields = ('key', 'title', 'description', 'banner', 'banner_static_path', 'content', 'settings', 'active', 'order')


@admin.register(Campaign)
class CampaignAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'slug', 'status', 'is_active', 'updated_at', 'open_stats', 'copy_link')
    list_filter = ('status', 'is_active')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'archived_at')
    actions = ('activate_campaigns', 'disable_campaigns', 'archive_campaigns', 'duplicate_campaigns')
    inlines = (CampaignPageInline,)
    fieldsets = (
        ('بيانات الحملة', {
            'fields': ('name', 'slug', 'description', 'status', 'is_active', 'archived_at'),
        }),
        ('الهوية البصرية', {
            'fields': (
                'logo',
                'logo_static_path',
                'splash_image',
                'splash_static_path',
                'background_image',
                'background_static_path',
            ),
        }),
        ('الألوان والنصوص الرئيسية', {
            'fields': (
                'primary_color',
                'secondary_color',
                'accent_color',
                'color_settings',
                'main_title',
                'main_description',
                'welcome_text',
            ),
        }),
        ('الإعدادات الديناميكية', {
            'fields': ('doctor_settings', 'qr_settings', 'deep_link_settings', 'page_settings'),
            'classes': ('collapse',),
        }),
        ('التواريخ', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:campaign_id>/activate/', self.admin_site.admin_view(self.activate_view), name='campaigns_campaign_activate'),
            path('<int:campaign_id>/duplicate/', self.admin_site.admin_view(self.duplicate_view), name='campaigns_campaign_duplicate'),
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view), name='campaigns_dashboard'),
            path('qr/<int:location_id>/png/', self.admin_site.admin_view(self.qr_png_view), name='campaigns_qr_location_png'),
        ]
        return custom_urls + urls

    def open_stats(self, obj):
        url = reverse('admin:campaigns_dashboard')
        return format_html('<a href="{}?campaign={}">الإحصائيات</a>', url, obj.pk)

    open_stats.short_description = 'الإحصائيات'

    def copy_link(self, obj):
        if not obj.pk:
            return '-'
        url = reverse('admin:campaigns_campaign_duplicate', kwargs={'campaign_id': obj.pk})
        return format_html('<a href="{}">نسخ</a>', url)

    copy_link.short_description = 'نسخ'

    def activate_view(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        campaign.activate()
        self.message_user(request, f'تم تفعيل حملة {campaign.name}.', messages.SUCCESS)
        return self.response_post_save_change(request, campaign)

    def duplicate_view(self, request, campaign_id):
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        duplicate = campaign.duplicate()
        self.message_user(request, f'تم نسخ حملة {campaign.name} إلى {duplicate.name}.', messages.SUCCESS)
        return self.response_post_save_change(request, duplicate)

    def activate_campaigns(self, request, queryset):
        count = 0
        for campaign in queryset:
            campaign.activate()
            count += 1
        self.message_user(request, f'تم تفعيل {count} حملة. تبقى آخر حملة محددة هي النشطة فقط.')

    activate_campaigns.short_description = 'تفعيل الحملات المحددة'

    def disable_campaigns(self, request, queryset):
        for campaign in queryset:
            campaign.disable()
        self.message_user(request, f'تم تعطيل {queryset.count()} حملة.')

    disable_campaigns.short_description = 'تعطيل الحملات المحددة'

    def archive_campaigns(self, request, queryset):
        for campaign in queryset:
            campaign.archive()
        self.message_user(request, f'تمت أرشفة {queryset.count()} حملة.')

    archive_campaigns.short_description = 'أرشفة الحملات المحددة'

    def duplicate_campaigns(self, request, queryset):
        for campaign in queryset:
            campaign.duplicate()
        self.message_user(request, f'تم نسخ {queryset.count()} حملة.')

    duplicate_campaigns.short_description = 'نسخ الحملات المحددة'

    def dashboard_view(self, request):
        campaign_id = request.GET.get('campaign')
        campaign = Campaign.objects.filter(pk=campaign_id).first() if campaign_id else get_active_campaign()
        all_stats = campaign_stats()
        active_stats = campaign_stats(campaign) if campaign else campaign_stats()
        campaigns = Campaign.objects.annotate(total_interactions=Count('interactions')).order_by('-is_active', 'name')
        qr_locations = QrLocation.objects.all()
        if campaign and any(field.name == 'campaign' for field in QrLocation._meta.fields):
            qr_locations = qr_locations.filter(campaign=campaign)
        context = {
            **self.admin_site.each_context(request),
            'title': 'لوحة إحصائيات الحملات',
            'campaign': campaign,
            'campaigns': campaigns,
            'active_stats': active_stats,
            'all_stats': all_stats,
            'qr_locations': qr_locations.order_by('city', 'name')[:50],
        }
        return TemplateResponse(request, 'admin/campaigns/dashboard.html', context)

    def qr_png_view(self, request, location_id):
        location = get_object_or_404(QrLocation, pk=location_id)
        image_bytes = generate_qr_png(build_qr_location_url(request, location))
        response = HttpResponse(image_bytes, content_type='image/png')
        disposition = 'attachment' if request.GET.get('download') == '1' else 'inline'
        response['Content-Disposition'] = f'{disposition}; filename="qr-{location.slug}-print.png"'
        return response


@admin.register(CampaignPage)
class CampaignPageAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'campaign', 'key', 'active', 'order')
    list_filter = ('campaign', 'active')
    search_fields = ('title', 'description', 'key')
    list_editable = ('active', 'order')
    inlines = (CampaignButtonInline,)


@admin.register(CampaignButton)
class CampaignButtonAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('label', 'campaign', 'page', 'action_type', 'order', 'active')
    list_filter = ('campaign', 'action_type', 'active')
    search_fields = ('label', 'url', 'deep_link')
    list_editable = ('order', 'active')


@admin.register(CampaignInteraction)
class CampaignInteractionAdmin(ActiveCampaignAdminMixin, admin.ModelAdmin):
    list_display = ('event_type', 'campaign', 'visitor_id', 'path', 'created_at')
    list_filter = ('campaign', 'event_type', 'created_at')
    search_fields = ('visitor_id', 'path')
    readonly_fields = ('campaign', 'event_type', 'visitor_id', 'path', 'metadata', 'created_at')

    def has_add_permission(self, request):
        return False
