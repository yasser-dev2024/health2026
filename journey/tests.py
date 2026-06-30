from datetime import date

from django.test import TestCase

from events.models import HealthEvent
from locations.models import HealthLocation

from .services import build_daily_plan


class JourneyPlanServiceTests(TestCase):
    def setUp(self):
        HealthEvent.objects.create(
            title='فعالية توعوية',
            description='نصائح صحية',
            city='أبها',
            location='المركز',
            date=date(2026, 7, 1),
            time='07:00 ص',
            category='توعية',
            active=True,
        )
        HealthLocation.objects.create(
            name='طوارئ أبها',
            location_type=HealthLocation.TYPE_EMERGENCY,
            city='أبها',
            phone='997',
            active=True,
        )
        HealthLocation.objects.create(
            name='مركز صحي أبها',
            location_type=HealthLocation.TYPE_HEALTH_CENTER,
            city='أبها',
            phone='937',
            active=True,
        )
        HealthLocation.objects.create(
            name='ممشى صحي',
            location_type=HealthLocation.TYPE_WALKWAY,
            city='أبها',
            active=True,
        )

    def test_urgent_answers_return_emergency_plan(self):
        plan = build_daily_plan(
            {
                'current_location': 'abha',
                'age_group': 'adult',
                'party_type': 'individual',
                'visit_purpose': 'urgent',
                'has_health_condition': False,
            }
        )

        self.assertEqual(plan['risk_level'], 'عاجل')
        self.assertIn('997', ' '.join(plan['tips']))
        self.assertEqual(plan['health_center'].location_type, HealthLocation.TYPE_EMERGENCY)

    def test_senior_answers_get_safe_recommendations(self):
        plan = build_daily_plan(
            {
                'current_location': 'abha',
                'age_group': 'elderly',
                'party_type': 'individual',
                'visit_purpose': 'relax',
                'has_health_condition': False,
            }
        )

        self.assertEqual(plan['risk_level'], 'اعتيادي')
        self.assertIn('مسارا قصيرا', plan['tips'][0])

# Create your tests here.
