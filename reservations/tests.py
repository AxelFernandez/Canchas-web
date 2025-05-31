from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta, datetime
from venues.models import Venue
from courts.models import Court, CourtType, TurnDuration
from .models import Reservation
from .forms import ReservationForm

User = get_user_model()

class ReservationLogicTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.venue_owner = User.objects.create_user(username='resowner', password='pw', is_venue_owner=True)
        cls.client_user = User.objects.create_user(username='client1', password='pw')
        cls.venue = Venue.objects.create(owner=cls.venue_owner, name='Reservation Venue')
        cls.court_type = CourtType.objects.create(name='BookingType') # Ensure this is created once
        cls.court = Court.objects.create(venue=cls.venue, name='Bookable Court', court_type=cls.court_type, is_active=True)
        TurnDuration.objects.create(court=cls.court, duration_minutes=60)

        # A reservation for "tomorrow" at 10 AM
        cls.tomorrow = timezone.now().date() + timedelta(days=1)
        cls.existing_reservation_time = timezone.make_aware(datetime.combine(cls.tomorrow, datetime.strptime("10:00", "%H:%M").time()))
        Reservation.objects.create(
            court=cls.court,
            user=cls.venue_owner, # some other user
            start_time=cls.existing_reservation_time,
            # end_time is auto-calculated by model's save method
        )

    def test_court_availability_view(self):
        self.client.login(username='client1', password='pw')
        url = reverse('reservations:court-availability', kwargs={'court_pk': self.court.pk})
        response = self.client.get(url, {'date': self.tomorrow.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.court.name)

        # Example: Check if 09:00 is available and 10:00 is booked
        # Timezone needs to be consistent. start_time_iso from view is aware.
        slot_0900_dt_naive = datetime.combine(self.tomorrow, datetime.strptime("09:00", "%H:%M").time())
        slot_0900_dt_aware = timezone.make_aware(slot_0900_dt_naive, timezone.get_default_timezone())
        slot_0900_iso = slot_0900_dt_aware.isoformat()

        # existing_reservation_time is already aware
        slot_1000_iso = self.existing_reservation_time.isoformat()

        # Construct the expected URL part for the "Book Now" link
        # Note: The domain "http://testserver" is added by Django test client internally.
        # We need to ensure the query parameters are correctly encoded if they contain special characters.
        # For ISO format datetime, it should be fine.
        book_now_url_0900 = f"{reverse('reservations:reservation-create', kwargs={'court_pk': self.court.pk})}?start_time={slot_0900_iso}"
        book_now_url_1000 = f"{reverse('reservations:reservation-create', kwargs={'court_pk': self.court.pk})}?start_time={slot_1000_iso}"

        self.assertContains(response, f'href="{book_now_url_0900}"')
        # For the booked slot, the "Book Now" link should NOT be present.
        # The template shows "(Booked)" text instead.
        self.assertNotContains(response, f'href="{book_now_url_1000}"')
        self.assertContains(response, "(Booked)") # Check that the 10:00 slot is marked as booked


    def test_reservation_create_view_permissions(self):
        # Anonymous user should be redirected to login
        self.client.logout()
        # A valid future time slot
        slot_to_book_time_naive = datetime.combine(self.tomorrow, datetime.strptime("14:00", "%H:%M").time())
        slot_to_book_time_aware = timezone.make_aware(slot_to_book_time_naive, timezone.get_default_timezone())

        url = reverse('reservations:reservation-create', kwargs={'court_pk': self.court.pk}) + f'?start_time={slot_to_book_time_aware.isoformat()}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(reverse('login') in response.url)

    def test_reservation_form_double_booking(self):
        # Try to book the already booked 10 AM slot
        form_data = {
            'start_time': self.existing_reservation_time,
            'court_id': str(self.court.pk), # Ensure it's a string as per form field
            'notes': 'Trying to double book'
        }
        # Pass the court object to the form as it's used in form's clean method
        form = ReservationForm(data=form_data, court=self.court)
        self.assertFalse(form.is_valid())
        self.assertIn('This time slot is no longer available', form.errors.get('__all__')[0])

    def test_reservation_form_book_in_past(self):
        past_time = timezone.now() - timedelta(hours=1)
        form_data = {'start_time': past_time, 'court_id': str(self.court.pk)}
        form = ReservationForm(data=form_data, court=self.court)
        self.assertFalse(form.is_valid())
        self.assertIn('Cannot book a reservation in the past', form.errors.get('start_time')[0])

    def test_successful_reservation_creation(self):
        self.client.login(username='client1', password='pw')
        # A valid future time slot (e.g., tomorrow 11 AM)
        slot_to_book_time_naive = datetime.combine(self.tomorrow, datetime.strptime("11:00", "%H:%M").time())
        slot_to_book_time_aware = timezone.make_aware(slot_to_book_time_naive, timezone.get_default_timezone())

        create_url = reverse('reservations:reservation-create', kwargs={'court_pk': self.court.pk})

        # GET the form first to ensure context is fine
        response_get = self.client.get(create_url + f'?start_time={slot_to_book_time_aware.isoformat()}')
        self.assertEqual(response_get.status_code, 200)

        # POST to create reservation
        response_post = self.client.post(create_url, {
            'start_time': slot_to_book_time_aware.isoformat(),
            'court_id': str(self.court.pk),
            'notes': 'My test reservation'
        })

        self.assertEqual(response_post.status_code, 302, response_post.content.decode())
        self.assertTrue(Reservation.objects.filter(user=self.client_user, court=self.court, start_time=slot_to_book_time_aware).exists())

    def test_user_reservation_list_view(self):
        self.client.login(username='client1', password='pw')
        # Create a reservation for this client_user first
        my_reservation_time_naive = datetime.combine(self.tomorrow, datetime.strptime("15:00", "%H:%M").time())
        my_reservation_time_aware = timezone.make_aware(my_reservation_time_naive, timezone.get_default_timezone())
        Reservation.objects.create(user=self.client_user, court=self.court, start_time=my_reservation_time_aware)

        response = self.client.get(reverse('reservations:my-reservations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.court.name)
        # Check for time part, format might depend on template filter
        self.assertContains(response, my_reservation_time_aware.strftime('%H:%M'))
