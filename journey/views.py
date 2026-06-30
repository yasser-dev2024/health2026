from django.shortcuts import redirect, render

from core.utils import get_visitor_id

from .forms import JourneyForm
from .models import JourneySubmission
from .services import build_daily_plan


def journey_view(request):
    form = JourneyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        visitor_id = get_visitor_id(request)
        answers = form.cleaned_data
        request.session['journey_answers'] = answers
        JourneySubmission.objects.create(visitor_id=visitor_id, **answers)
        return redirect('plan')

    return render(request, 'journey/form.html', {'form': form})


def plan_view(request):
    answers = request.session.get('journey_answers')
    plan = build_daily_plan(answers) if answers else None

    return render(
        request,
        'journey/plan.html',
        {
            'answers': answers,
            'plan': plan,
        },
    )

# Create your views here.
