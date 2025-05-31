from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Venue

User = get_user_model()

class VenueManagementTests(TestCase):
    def setUp(self):
        self.venue_owner = User.objects.create_user(username='owner1', password='password', is_venue_owner=True)
        self.regular_user = User.objects.create_user(username='user1', password='password')

        self.venue1 = Venue.objects.create(owner=self.venue_owner, name='Owner1 Venue', address='123 Main St')

    def test_venue_list_view_permissions(self):
        # Regular user should not access venue list (owner dashboard)
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('venues:venue-list'))
        self.assertEqual(response.status_code, 403) # Forbidden

        # Venue owner should access
        self.client.login(username='owner1', password='password')
        response = self.client.get(reverse('venues:venue-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.venue1.name)

    def test_venue_create_view_permissions(self):
        self.client.login(username='user1', password='password')
        response = self.client.get(reverse('venues:venue-create'))
        self.assertEqual(response.status_code, 403)

        self.client.login(username='owner1', password='password')
        response = self.client.get(reverse('venues:venue-create'))
        self.assertEqual(response.status_code, 200)

    def test_venue_update_view_permissions(self):
        # Other venue owner cannot update venue1
        other_owner = User.objects.create_user(username='owner2', password='password', is_venue_owner=True)
        self.client.login(username='owner2', password='password')
        response = self.client.get(reverse('venues:venue-update', kwargs={'pk': self.venue1.pk}))
        self.assertEqual(response.status_code, 404) # Or 403 if queryset returns None leading to 404

        # Correct owner can access
        self.client.login(username='owner1', password='password')
        response = self.client.get(reverse('venues:venue-update', kwargs={'pk': self.venue1.pk}))
        self.assertEqual(response.status_code, 200)

    def test_venue_public_views(self):
        # Public list view should be accessible to anonymous users
        self.client.logout()
        response = self.client.get(reverse('venues:venue-public-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.venue1.name)

        response = self.client.get(reverse('venues:venue-public-detail', kwargs={'pk': self.venue1.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.venue1.name)
