import re

from django.db.models import F
from django.utils import timezone

from campaigns.services import campaign_queryset, get_active_campaign

from .models import DoctorAssistantQuestion, KeywordAnswer

DIACRITICS_RE = re.compile(r'[\u064B-\u065F\u0670\u0640]')
NON_WORD_RE = re.compile(r'[^\u0600-\u06FFa-z0-9\s]')
SPACE_RE = re.compile(r'\s+')

EMERGENCY_TERMS = [
    'الم صدر',
    'اختناق',
    'نزيف',
    'فقدان وعي',
    'صعوبه تنفس',
    'ضيق تنفس',
    'اغماء',
]

EMERGENCY_RESPONSE = (
    'قد تكون هذه حالة طارئة. اتصل فورا بالإسعاف 997، أو تواصل مع 937 '
    'للاستشارة الصحية، وتوجه لأقرب طوارئ عند وجود ألم صدر أو صعوبة تنفس أو نزيف.'
)


def normalize_arabic(value):
    value = (value or '').lower()
    value = re.sub(r'[أإآٱ]', 'ا', value)
    value = value.replace('ة', 'ه').replace('ى', 'ي')
    value = DIACRITICS_RE.sub('', value)
    value = NON_WORD_RE.sub(' ', value)
    return SPACE_RE.sub(' ', value).strip()


def _score(normalized_input, question, keywords):
    terms = [question, *(keywords or [])]
    input_tokens = set(normalized_input.split())
    score = 0
    for term in terms:
        normalized_term = normalize_arabic(term)
        if not normalized_term:
            continue
        if normalized_term in normalized_input:
            score += 8
            continue
        term_tokens = normalized_term.split()
        score += len([token for token in term_tokens if token in input_tokens])
    return score


def _touch(model, pk):
    model.objects.filter(pk=pk).update(
        usage_count=F('usage_count') + 1,
        last_used_at=timezone.now(),
    )


def answer_query(query, campaign=None):
    normalized = normalize_arabic(query)
    if any(term in normalized for term in EMERGENCY_TERMS):
        return {
            'is_emergency': True,
            'answer': EMERGENCY_RESPONSE,
            'matched': None,
            'confidence': 99,
        }

    best = {'score': 0, 'kind': None, 'object': None}

    keyword_answers = KeywordAnswer.objects.filter(active=True)
    doctor_questions = DoctorAssistantQuestion.objects.filter(active=True)
    if campaign is not None:
        keyword_answers = campaign_queryset(keyword_answers, campaign=campaign)
        doctor_questions = campaign_queryset(doctor_questions, campaign=campaign)
    elif keyword_answers.filter(campaign__isnull=True).exists() or doctor_questions.filter(campaign__isnull=True).exists():
        keyword_answers = keyword_answers.filter(campaign__isnull=True)
        doctor_questions = doctor_questions.filter(campaign__isnull=True)
    else:
        active_campaign = get_active_campaign()
        keyword_answers = campaign_queryset(keyword_answers, campaign=active_campaign)
        doctor_questions = campaign_queryset(doctor_questions, campaign=active_campaign)

    for answer in keyword_answers:
        score = _score(normalized, answer.question, answer.keywords)
        if score and score >= best['score']:
            best = {'score': score, 'kind': 'keyword', 'object': answer}

    for question in doctor_questions:
        score = _score(normalized, question.question, question.keywords)
        if score and score >= best['score']:
            best = {'score': score, 'kind': 'question', 'object': question}

    if not best['object']:
        return {
            'is_emergency': False,
            'answer': 'لم أجد إجابة دقيقة. جرّب كلمات مثل: مركز صحي، طوارئ، ترطيب، فعاليات، أو اتصل بـ 937 للاستشارة.',
            'matched': None,
            'confidence': 0,
        }

    matched = best['object']
    if best['kind'] == 'keyword':
        _touch(KeywordAnswer, matched.pk)
        return {
            'is_emergency': False,
            'answer': matched.answer,
            'matched': matched,
            'confidence': best['score'],
            'cta_label': matched.cta_label,
            'cta_url': matched.cta_url,
            'link_label': matched.link_label,
            'link_url': matched.link_url,
        }

    _touch(DoctorAssistantQuestion, matched.pk)
    return {
        'is_emergency': False,
        'answer': matched.answer,
        'matched': matched,
        'confidence': best['score'],
        'cta_label': matched.cta_label,
        'cta_url': matched.cta_url,
        'link_label': matched.link_label,
        'link_url': matched.link_url,
    }
