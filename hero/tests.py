from django.test import Client, TestCase
from django.urls import reverse

from .models import HealthHeroEntry, HealthHeroQuestion


class HealthHeroTests(TestCase):
    def test_hero_challenge_records_score(self):
        HealthHeroQuestion.objects.all().delete()
        first = HealthHeroQuestion.objects.create(
            question='سؤال 1',
            options=['أ', 'ب'],
            correct_index=1,
            result_message='صحيح',
            active=True,
            order=1,
        )
        second = HealthHeroQuestion.objects.create(
            question='سؤال 2',
            options=['أ', 'ب'],
            correct_index=0,
            result_message='صحيح',
            active=True,
            order=2,
        )

        response = Client().post(
            reverse('hero'),
            {
                f'question_{first.pk}': '1',
                f'question_{second.pk}': '1',
                'participant_name': 'سارة',
                'phone': '0500000000',
            },
        )

        self.assertEqual(response.status_code, 200)
        entry = HealthHeroEntry.objects.get()
        self.assertEqual(entry.score, 15)
        self.assertEqual(entry.total, 30)
        self.assertEqual(entry.participant_name, 'سارة')
        self.assertEqual(entry.phone, '0500000000')

# Create your tests here.
