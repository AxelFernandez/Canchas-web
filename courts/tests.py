from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from venues.models import Venue
from .models import Court, CourtType, TurnDuration

User = get_user_model()

class CourtManagementTests(TestCase):
    def setUp(self):
        self.venue_owner = User.objects.create_user(username='courtowner', password='password', is_venue_owner=True)
        self.other_owner = User.objects.create_user(username='othercourtowner', password='password', is_venue_owner=True)
        self.regular_user = User.objects.create_user(username='courtuser', password='password')

        self.venue = Venue.objects.create(owner=self.venue_owner, name='Test Venue for Courts', address='456 Court Ave')
        self.other_venue = Venue.objects.create(owner=self.other_owner, name='Other Venue', address='789 Other St')

        self.padel_type = CourtType.objects.create(name='Padel Test')
        self.court1 = Court.objects.create(venue=self.venue, name='Padel Court 1', court_type=self.padel_type)
        TurnDuration.objects.create(court=self.court1, duration_minutes=90)

    def test_court_list_view_permissions(self):
        self.client.login(username='courtuser', password='password')
        response = self.client.get(reverse('courts:court-list', kwargs={'venue_pk': self.venue.pk}))
        self.assertEqual(response.status_code, 403) # Regular user forbidden

        self.client.login(username='othercourtowner', password='password')
        response = self.client.get(reverse('courts:court-list', kwargs={'venue_pk': self.venue.pk}))
        self.assertEqual(response.status_code, 404) # Other owner, venue not theirs -> 404

        self.client.login(username='courtowner', password='password')
        response = self.client.get(reverse('courts:court-list', kwargs={'venue_pk': self.venue.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.court1.name)

    def test_court_create_view_permissions(self):
        self.client.login(username='courtowner', password='password')
        response = self.client.get(reverse('courts:court-create', kwargs={'venue_pk': self.venue.pk}))
        self.assertEqual(response.status_code, 200)

    def test_turn_duration_default_creation(self):
        self.client.login(username='courtowner', password='password')
        court_data = {'name': 'New Test Court', 'court_type': self.padel_type.pk}
        self.client.post(reverse('courts:court-create', kwargs={'venue_pk': self.venue.pk}), court_data)
        new_court = Court.objects.get(name='New Test Court')
        self.assertTrue(TurnDuration.objects.filter(court=new_court).exists())
        self.assertEqual(new_court.turn_duration_setting.duration_minutes, 60) # Default

    def test_court_detail_view_shows_turn_duration_form(self):
        self.client.login(username='courtowner', password='password')
        response = self.client.get(reverse('courts:court-detail', kwargs={'pk': self.court1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Update Duration') # Button for form
        self.assertIn('turn_duration_form', response.context)
