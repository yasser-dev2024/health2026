from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render

from .models import AwarenessContent, AwarenessMessage


def downloads_view(request):
    content_id = request.GET.get('download')
    if content_id:
        content = get_object_or_404(AwarenessContent, pk=content_id, active=True)
        AwarenessContent.objects.filter(pk=content.pk).update(download_count=F('download_count') + 1)
        file_src = content.get_file_src()
        if file_src:
            return redirect(file_src)

    active_type = request.GET.get('type', 'all')
    contents = AwarenessContent.objects.filter(active=True).order_by('order', 'title')
    if active_type != 'all':
        contents = contents.filter(content_type=active_type)

    type_counts = {
        'all': AwarenessContent.objects.filter(active=True).count(),
        'pdf': AwarenessContent.objects.filter(active=True, content_type='pdf').count(),
        'card': AwarenessContent.objects.filter(active=True, content_type='card').count(),
        'post': AwarenessContent.objects.filter(active=True, content_type='post').count(),
        'link': AwarenessContent.objects.filter(active=True, content_type='link').count(),
    }

    return render(request, 'awareness/downloads.html', {
        'contents': contents,
        'active_type': active_type,
        'type_counts': type_counts,
    })


def messages_view(request):
    messages = AwarenessMessage.objects.filter(active=True).order_by('order', 'id')
    return render(request, 'awareness/messages.html', {'messages': messages})
