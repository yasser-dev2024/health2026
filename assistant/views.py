from django.shortcuts import render

from .forms import AssistantQueryForm
from .models import DoctorAssistantQuestion
from .services import answer_query


def assistant_view(request):
    result = None
    form = AssistantQueryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        result = answer_query(form.cleaned_data['query'])

    questions = DoctorAssistantQuestion.objects.filter(active=True).order_by('order', 'question')[:6]
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
