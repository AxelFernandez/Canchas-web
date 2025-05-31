from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAuthenticationTests(TestCase):

    def setUp(self):
        self.user_credentials = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'testuser@example.com'
        }
        self.venue_owner_credentials = {
            'username': 'venueowner',
            'password': 'testpassword456',
            'email': 'venueowner@example.com',
            'is_venue_owner': True
        }
        self.user = User.objects.create_user(**self.user_credentials)
        self.venue_owner = User.objects.create_user(**self.venue_owner_credentials)

    def test_user_signup_and_login(self):
        # Test signup page loads
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)

        # Test user creation via form (simplified, more detailed form tests could be added)
        # signup_data = {'username': 'newbie', 'password': 'newpassword123', 'password2': 'newpassword123', 'is_venue_owner': False}
        # Assuming CustomUserCreationForm fields for password confirmation etc.
        # This test is more about the view. Actual form validation should be in form tests.
        # response = self.client.post(reverse('signup'), signup_data)
        # self.assertEqual(response.status_code, 302) # Redirects to login
        # self.assertTrue(User.objects.filter(username='newbie').exists())

        # Test login page loads
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

        # Test user login
        login_response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpassword123'})
        self.assertEqual(login_response.status_code, 302) # Redirects on successful login
        self.assertIn('_auth_user_id', self.client.session)

    def test_venue_owner_property(self):
        self.assertFalse(self.user.is_venue_owner)
        self.assertTrue(self.venue_owner.is_venue_owner)
