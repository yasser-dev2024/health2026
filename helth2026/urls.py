"""
URL configuration for helth2026 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from assistant import views as assistant_views
from awareness import views as awareness_views
from campaigns import views as campaign_views
from dashboard import views as dashboard_views
from hero import views as hero_views
from journey import views as journey_views
from locations import views as location_views
from passport import views as passport_views
from qr import views as qr_views

admin.site.site_header = 'لوحة إدارة صيف وصحة'
admin.site.site_title = 'إدارة صيف وصحة'
admin.site.index_title = 'لوحة الإدارة'

urlpatterns = [
    path('', include('core.urls')),
    path('journey/', include('journey.urls')),
    path('plan/', journey_views.plan_view, name='plan'),
    path('events/', include('events.urls')),
    path('passport/', passport_views.passport_view, name='passport'),
    path('downloads/', awareness_views.downloads_view, name='downloads'),
    path('messages/', awareness_views.messages_view, name='messages'),
    path('assistant/', assistant_views.assistant_view, name='assistant'),
    path('nearby/', location_views.nearby_view, name='nearby'),
    path('hero/', hero_views.hero_view, name='hero'),
    path('pages/<slug:page_key>/', campaign_views.campaign_page_view, name='campaign_page'),
    path('qr/profile/', qr_views.qr_profile_view, name='qr_profile'),
    path('qr/<slug:slug>/', qr_views.qr_location_view, name='qr_location'),
    path('qr-item/<int:item_id>/', qr_views.qr_item_view, name='qr_item'),
    path('admin/login/', dashboard_views.AdminLoginView.as_view(), name='admin_login'),
    path('admin/logout/', dashboard_views.logout_view, name='admin_logout'),
    path('admin/downloads/', dashboard_views.admin_downloads_view, name='admin_downloads'),
    path('admin/messages/', dashboard_views.admin_messages_view, name='admin_messages'),
    path('admin/events/', dashboard_views.admin_events_view, name='admin_events'),
    path('admin/locations/', dashboard_views.admin_locations_view, name='admin_locations'),
    path('admin/qr-locations/', dashboard_views.qr_locations_view, name='admin_qr_locations'),
    path('admin/qr-locations/<int:location_id>/png/', dashboard_views.qr_location_png_view, name='admin_qr_location_png'),
    path('admin/', dashboard_views.dashboard_view, name='admin_dashboard'),
    path('django-admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
