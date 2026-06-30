from django.shortcuts import render

from campaigns.services import campaign_queryset, get_active_campaign

from .forms import HeroChallengeForm
from .models import HealthHeroQuestion
from .services import POINTS_PER_CORRECT_ANSWER, evaluate_answers


def _question_payload(questions):
    return [
        {
            'id': question.pk,
            'question': question.question,
            'options': question.options,
            'correctIndex': question.correct_index,
            'resultMessage': question.result_message,
            'tip': question.tip,
        }
        for question in questions
    ]


def hero_view(request):
    campaign = get_active_campaign()
    questions = list(campaign_queryset(HealthHeroQuestion.objects.filter(active=True), campaign=campaign).order_by('order', 'id'))
    form = HeroChallengeForm(request.POST or None)
    entry = None
    if request.method == 'POST' and form.is_valid():
        entry = evaluate_answers(request, request.POST, form.cleaned_data)

    whatsapp_text = ''
    if entry:
        name = entry.participant_name or 'بطل الصحة'
        whatsapp_text = f'حصل {name} على شهادة {entry.badge_label} بنتيجة {entry.score}/{entry.total} في تحدي بطل الصحة في عسير'

    return render(
        request,
        'hero/hero.html',
        {
            'questions': questions,
            'hero_questions_json': _question_payload(questions),
            'entry': entry,
            'form': form,
            'points_per_answer': POINTS_PER_CORRECT_ANSWER,
            'total_points': len(questions) * POINTS_PER_CORRECT_ANSWER,
            'whatsapp_text': whatsapp_text,
        },
    )
