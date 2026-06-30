from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from passport.models import PassportStamp, VisitorPassport

from .models import QrItem, QrLocation, QrLocationVisit, QrScan, QrVisitorProfile


class QrServicesTests(TestCase):
    def test_qr_location_scan_is_recorded(self):
        location = QrLocation.objects.create(name='بوابة السودة', slug='soudah', active=True)
        response = Client().get(reverse('qr_location', kwargs={'slug': location.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(QrScan.objects.filter(qr_type=QrScan.TYPE_LOCATION).count(), 1)
        location.refresh_from_db()
        self.assertEqual(location.scans_count, 1)

    def test_home_qr_query_records_scan_without_ql_flag(self):
        location = QrLocation.objects.create(name='Art Street', slug='art-street', active=True)
        response = Client().get(f'/?qr={location.slug}&qrName=Art')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(QrScan.objects.filter(qr_type=QrScan.TYPE_LOCATION, qr_location=location).count(), 1)
        location.refresh_from_db()
        self.assertEqual(location.scans_count, 1)

    def test_qr_item_awards_stamp_once_and_counts_points(self):
        stamp = PassportStamp.objects.create(
            name='ختم الترطيب',
            slug='hydration-test',
            description='ختم اختبار',
            points=20,
            active=True,
        )
        item = QrItem.objects.create(title='نقطة الترطيب', stamp=stamp, active=True)
        client = Client()

        first = client.get(reverse('qr_item', kwargs={'item_id': item.id}))
        second = client.get(reverse('qr_item', kwargs={'item_id': item.id}))

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        passport = VisitorPassport.objects.get()
        self.assertEqual(passport.points, 20)
        self.assertEqual(passport.stamps.count(), 1)
        self.assertEqual(passport.scans_count, 2)
        self.assertEqual(QrScan.objects.filter(qr_type=QrScan.TYPE_ITEM).count(), 2)

    def test_same_visitor_same_location_is_not_counted_twice_within_ten_minutes(self):
        location = QrLocation.objects.create(name='مطار أبها', slug='airport', active=True)
        other_location = QrLocation.objects.create(name='شارع الفن', slug='artstreet', active=True)
        client = Client()

        client.get(f'/?qr={location.slug}')
        client.get(f'/?qr={location.slug}')
        client.get(f'/?qr={other_location.slug}')

        self.assertEqual(QrLocationVisit.objects.filter(qr_location=location).count(), 1)
        self.assertEqual(QrScan.objects.filter(qr_type=QrScan.TYPE_LOCATION, qr_location=location).count(), 1)
        self.assertEqual(QrLocationVisit.objects.filter(qr_location=other_location).count(), 1)
        location.refresh_from_db()
        other_location.refresh_from_db()
        self.assertEqual(location.scans_count, 1)
        self.assertEqual(other_location.scans_count, 1)

    def test_qr_profile_saves_optional_analytics_for_start_location(self):
        location = QrLocation.objects.create(name='ممشى الضباب', slug='dababwalk', active=True)
        client = Client()
        client.get(f'/?qr={location.slug}')

        response = client.post(
            reverse('qr_profile'),
            {
                'visitor_type': 'visitor',
                'party_type': 'family',
                'age_group': '18_30',
                'health_topic': 'blood_pressure',
            },
        )

        self.assertEqual(response.status_code, 200)
        profile = QrVisitorProfile.objects.get()
        self.assertEqual(profile.qr_location, location)
        self.assertEqual(profile.visitor_type, 'visitor')
        self.assertEqual(profile.party_type, 'family')
        self.assertEqual(profile.age_group, '18_30')
        self.assertEqual(profile.health_topic, 'blood_pressure')


class QrAdminWorkflowTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_superuser('admin', 'admin@example.com', 'Admin@2026')
        self.client.force_login(self.admin)

    def test_admin_qr_create_form_is_simple_and_visible_from_button(self):
        response = self.client.get(reverse('admin_qr_locations'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'إنشاء QR جديد')
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, 'name="active"')
        self.assertNotContains(response, 'name="slug"')
        self.assertNotContains(response, 'name="category"')

    def test_admin_can_create_scan_edit_download_and_delete_location_qr(self):
        create_response = self.client.post(
            reverse('admin_qr_locations'),
            {
                'action': 'save',
                'name': 'شارع الفن',
                'description': 'موقع حملة',
                'active': 'True',
            },
            follow=True,
        )

        self.assertEqual(create_response.status_code, 200)
        location = QrLocation.objects.get(slug='art-street')
        self.assertContains(create_response, '?qr=art-street')

        png_response = self.client.get(reverse('admin_qr_location_png', kwargs={'location_id': location.id}))
        self.assertEqual(png_response.status_code, 200)
        self.assertEqual(png_response['Content-Type'], 'image/png')
        self.assertGreater(len(png_response.content), 1000)

        mobile_client = Client(HTTP_USER_AGENT='Mobile Safari')
        scan_response = mobile_client.get(f'/?qr={location.slug}')
        self.assertEqual(scan_response.status_code, 200)
        self.assertEqual(QrLocationVisit.objects.filter(qr_location=location).count(), 1)
        location.refresh_from_db()
        self.assertEqual(location.scans_count, 1)

        admin_response = self.client.get(reverse('admin_qr_locations'))
        self.assertContains(admin_response, 'السودة')
        self.assertContains(admin_response, '1')

        edit_response = self.client.post(
            reverse('admin_qr_locations'),
            {
                'action': 'save',
                'location_id': location.id,
                'name': 'شارع الفن المطور',
                'description': 'موقع حملة محدث',
                'active': 'True',
            },
            follow=True,
        )
        self.assertEqual(edit_response.status_code, 200)
        location.refresh_from_db()
        self.assertEqual(location.name, 'شارع الفن المطور')
        user_response = Client().get(f'/?qr={location.slug}')
        self.assertEqual(user_response.context['qr_welcome_location'].name, 'شارع الفن المطور')

        delete_response = self.client.post(
            reverse('admin_qr_locations'),
            {'action': 'delete', 'location_id': location.id},
            follow=True,
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(QrLocation.objects.filter(pk=location.pk).exists())

        refresh_response = self.client.get(reverse('admin_qr_locations'))
        self.assertNotContains(refresh_response, 'QR art-street')
        self.assertEqual(self.client.get(reverse('admin_qr_location_png', kwargs={'location_id': location.id})).status_code, 404)

# Create your tests here.
