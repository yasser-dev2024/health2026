from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from campaigns.services import campaign_queryset, get_active_campaign, record_campaign_interaction

from .models import AwarenessContent, AwarenessMessage


def downloads_view(request):
    campaign = get_active_campaign()
    content_id = request.GET.get('download')
    if content_id:
        content = get_object_or_404(
            campaign_queryset(AwarenessContent.objects.filter(pk=content_id, active=True), campaign=campaign)
        )
        AwarenessContent.objects.filter(pk=content.pk).update(download_count=F('download_count') + 1)
        record_campaign_interaction(request, 'interaction', campaign=campaign, action='download', content_id=content.pk)
        file_src = content.get_file_src()
        if file_src:
            return redirect(file_src)

    active_type = request.GET.get('type', 'all')
    base_contents = campaign_queryset(AwarenessContent.objects.filter(active=True), campaign=campaign)
    contents = base_contents.order_by('order', 'title')
    if active_type != 'all':
        contents = contents.filter(content_type=active_type)

    type_counts = {
        'all': base_contents.count(),
        'pdf': base_contents.filter(content_type='pdf').count(),
        'card': base_contents.filter(content_type='card').count(),
        'post': base_contents.filter(content_type='post').count(),
        'link': base_contents.filter(content_type='link').count(),
    }

    return render(request, 'awareness/downloads.html', {
        'contents': contents,
        'active_type': active_type,
        'type_counts': type_counts,
    })


def messages_view(request):
    campaign = get_active_campaign()
    messages = campaign_queryset(AwarenessMessage.objects.filter(active=True), campaign=campaign).order_by('order', 'id')
    return render(request, 'awareness/messages.html', {'messages': messages})
