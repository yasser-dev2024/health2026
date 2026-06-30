from django.contrib.auth import get_user_model
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
        self.assertContains(response, 'data-phone="0500000000"')
        self.assertContains(response, 'class="certificate-name"')
        self.assertContains(response, 'سارة')

    def test_staff_can_open_saved_certificate(self):
        entry = HealthHeroEntry.objects.create(
            visitor_id='visitor-test',
            participant_name='ياسر',
            phone='0501894192',
            score=45,
            total=45,
            badge_label='أسطورة الصحة في عسير',
            answers={},
        )
        client = Client()

        response = client.get(reverse('hero_certificate', args=[entry.pk]))
        self.assertEqual(response.status_code, 302)

        user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='pass12345',
        )
        client.force_login(user)
        response = client.get(reverse('hero_certificate', args=[entry.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ياسر')
        self.assertContains(response, '0501894192')
        self.assertContains(response, 'data-hero-certificate')

# Create your tests here.
