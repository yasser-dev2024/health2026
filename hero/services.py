from core.utils import get_visitor_id
from campaigns.services import campaign_queryset, get_active_campaign, record_campaign_interaction

from .models import HealthHeroEntry, HealthHeroQuestion

POINTS_PER_CORRECT_ANSWER = 15


def badge_for_score(score, total):
    if total and score >= total * 0.9:
        return 'أسطورة الصحة في عسير'
    if total and score >= total * 0.7:
        return 'بطل الصحة'
    if total and score >= total * 0.5:
        return 'صديق الصحة'
    return 'مبتدئ صحي'


def evaluate_answers(request, posted_answers, contact_data=None):
    campaign = get_active_campaign()
    visitor_id = get_visitor_id(request)
    questions = list(campaign_queryset(HealthHeroQuestion.objects.filter(active=True), campaign=campaign).order_by('order', 'id'))
    score = 0
    details = {}
    for question in questions:
        raw_answer = posted_answers.get(f'question_{question.pk}')
        selected = int(raw_answer) if raw_answer and raw_answer.isdigit() else -1
        correct = selected == question.correct_index
        if correct:
            score += POINTS_PER_CORRECT_ANSWER
        details[str(question.pk)] = {
            'selected': selected,
            'correct': correct,
            'question': question.question,
            'tip': question.tip,
            'result_message': question.result_message,
        }

    participant_name = (contact_data or {}).get('participant_name', '').strip()
    phone = (contact_data or {}).get('phone', '').strip()
    total = len(questions) * POINTS_PER_CORRECT_ANSWER

    record_campaign_interaction(request, 'interaction', campaign=campaign, visitor_id=visitor_id, action='hero_challenge')
    return HealthHeroEntry.objects.create(
        campaign=campaign,
        visitor_id=visitor_id,
        participant_name=participant_name,
        phone=phone,
        score=score,
        total=total,
        badge_label=badge_for_score(score, total),
        answers=details,
    )
