from django.shortcuts import render

from campaigns.models import CampaignInteraction
from campaigns.services import campaign_queryset, get_active_campaign, record_campaign_interaction

from .forms import AssistantQueryForm
from .models import DoctorAssistantQuestion
from .services import answer_query


def assistant_view(request):
    campaign = get_active_campaign()
    record_campaign_interaction(request, CampaignInteraction.TYPE_ASSISTANT_OPEN, campaign=campaign)
    result = None
    form = AssistantQueryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        result = answer_query(form.cleaned_data['query'], campaign=campaign)
        record_campaign_interaction(
            request,
            CampaignInteraction.TYPE_ASSISTANT_QUERY,
            campaign=campaign,
            query=form.cleaned_data['query'][:180],
        )

    questions = campaign_queryset(
        DoctorAssistantQuestion.objects.filter(active=True),
        campaign=campaign,
    ).order_by('order', 'question')[:6]
    return render(
        request,
        'assistant/assistant.html',
        {
            'form': form,
            'result': result,
            'questions': questions,
        },
    )

# Create your views here.
