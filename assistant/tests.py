from django.test import TestCase

from .models import KeywordAnswer
from .services import answer_query, normalize_arabic


class AssistantServiceTests(TestCase):
    def test_normalize_arabic_unifies_common_forms(self):
        self.assertEqual(normalize_arabic('أَلَمُ  الصَّدْر'), 'الم الصدر')
        self.assertEqual(normalize_arabic('إرشادات آمنة'), 'ارشادات امنه')

    def test_emergency_response_mentions_emergency_numbers(self):
        result = answer_query('عندي ألم صدر وصعوبة تنفس')

        self.assertTrue(result['is_emergency'])
        self.assertIn('997', result['answer'])
        self.assertIn('937', result['answer'])

    def test_keyword_answer_is_matched_and_usage_is_recorded(self):
        answer = KeywordAnswer.objects.create(
            question='الترطيب',
            keywords=['ماء', 'دوخة'],
            answer='اشرب الماء وخذ استراحة.',
        )

        result = answer_query('أشعر بدوخة وأحتاج ماء')

        self.assertFalse(result['is_emergency'])
        self.assertEqual(result['matched'].pk, answer.pk)
        answer.refresh_from_db()
        self.assertEqual(answer.usage_count, 1)

# Create your tests here.
