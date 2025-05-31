from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import CreateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from datetime import datetime, timedelta, time as dt_time
from courts.models import Court
from .models import Reservation
from .forms import ReservationForm

class CourtAvailabilityView(View): # Not LoginRequired, anyone can view
    template_name = 'reservations/court_availability.html'

    def get(self, request, court_pk):
        court = get_object_or_404(Court, pk=court_pk, is_active=True)

        selected_date_str = request.GET.get('date', timezone.now().astimezone(timezone.get_default_timezone()).strftime('%Y-%m-%d'))
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = timezone.now().astimezone(timezone.get_default_timezone()).date()

        turn_duration_minutes = court.turn_duration_setting.duration_minutes

        opening_time = dt_time(8, 0)
        closing_time = dt_time(22, 0)

        time_slots = []
        # Combine selected_date with opening_time, then make it aware in default timezone
        current_dt_naive = datetime.combine(selected_date, opening_time)
        current_dt_aware = timezone.make_aware(current_dt_naive, timezone.get_default_timezone())

        end_of_operating_day_naive = datetime.combine(selected_date, closing_time)
        end_of_operating_day_aware = timezone.make_aware(end_of_operating_day_naive, timezone.get_default_timezone())

        reservations_on_date = Reservation.objects.filter(
            court=court,
            start_time__date=selected_date
        ) # These are aware datetimes from the DB

        booked_slot_start_times = {res.start_time for res in reservations_on_date}

        while current_dt_aware < end_of_operating_day_aware:
            slot_start_dt_aware = current_dt_aware
            slot_end_dt_aware = slot_start_dt_aware + timedelta(minutes=turn_duration_minutes)

            if slot_end_dt_aware > end_of_operating_day_aware:
                 # Special case: if closing_time is 23:59, slot_end_dt_aware might roll over to 00:00 of next day
                 if not (end_of_operating_day_aware.time() == dt_time(23,59,59,999999) and slot_end_dt_aware.time() == dt_time(0,0)): # approx
                    break

            is_booked = slot_start_dt_aware in booked_slot_start_times

            # Compare aware datetimes for past check
            is_past = slot_start_dt_aware < timezone.now()

            time_slots.append({
                'start_time_aware': slot_start_dt_aware, # Aware datetime object
                'end_time_aware': slot_end_dt_aware,     # Aware datetime object for end time
                'start_time_iso': slot_start_dt_aware.isoformat(), # For form pre-fill
                'is_booked': is_booked,
                'is_past': is_past,
            })
            current_dt_aware += timedelta(minutes=turn_duration_minutes)

        context = {
            'court': court,
            'selected_date': selected_date, # This is a date object
            'time_slots': time_slots,
            'previous_date': selected_date - timedelta(days=1),
            'next_date': selected_date + timedelta(days=1),
        }
        return render(request, self.template_name, context)


class ReservationCreateView(LoginRequiredMixin, CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'reservations/reservation_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        self.court = get_object_or_404(Court, pk=self.kwargs['court_pk'])
        kwargs['court'] = self.court # Pass court object to form

        if self.request.method == 'GET':
            start_time_iso_str = self.request.GET.get('start_time')
            initial_data = {'court_id': str(self.court.pk)} # court_id as string
            if start_time_iso_str:
                try:
                    # Parse ISO format string. Assume it's already in UTC or convert if it includes offset.
                    # For simplicity, if no offset, assume it's default timezone from previous view.
                    initial_start_time = datetime.fromisoformat(start_time_iso_str)

                    # Ensure it's aware. If it was naive, assume default timezone.
                    if timezone.is_naive(initial_start_time):
                         initial_start_time = timezone.make_aware(initial_start_time, timezone.get_default_timezone())
                    else: # if it has tzinfo, convert to default
                         initial_start_time = initial_start_time.astimezone(timezone.get_default_timezone())

                    initial_data['start_time'] = initial_start_time
                except ValueError:
                    # Handle error or let form validation catch it.
                    # Consider redirecting with an error message if start_time is crucial for form display.
                    pass
            kwargs['initial'] = initial_data
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        # The court object is already associated in the form's clean method if court_id is valid
        # If not, self.court (from get_form_kwargs) can be used as a fallback,
        # but the form should ideally handle court association via court_id.
        if not form.instance.court_id: # Should be set from hidden input
             form.instance.court = self.court

        # end_time calculation is handled by model's save method.
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['court'] = self.court # self.court from get_form_kwargs

        start_time_iso_str = self.request.GET.get('start_time')
        if start_time_iso_str:
            try:
                dt_obj = datetime.fromisoformat(start_time_iso_str)
                if timezone.is_naive(dt_obj): # Make aware if naive
                    dt_obj = timezone.make_aware(dt_obj, timezone.get_default_timezone())
                else: # Convert to default timezone if aware but different
                    dt_obj = dt_obj.astimezone(timezone.get_default_timezone())
                context['start_time_display'] = dt_obj.strftime('%Y-%m-%d %H:%M %Z')
            except ValueError:
                context['start_time_display'] = "Invalid time"
        else:
             context['start_time_display'] = "Not specified"
        return context

    def get_success_url(self):
        # Assuming 'my-reservations' is the correct name for UserReservationListView
        return reverse('reservations:my-reservations')


class UserReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations/user_reservation_list.html'
    context_object_name = 'reservations'
    paginate_by = 10

    def get_queryset(self):
        now = timezone.now()
        filter_type = self.request.GET.get('filter', 'upcoming')

        queryset = Reservation.objects.filter(user=self.request.user)
        if filter_type == 'upcoming':
            queryset = queryset.filter(start_time__gte=now).order_by('start_time')
        elif filter_type == 'past':
            queryset = queryset.filter(start_time__lt=now).order_by('-start_time')
        # Default to upcoming if filter_type is something else, or could add error handling
        else:
            queryset = queryset.filter(start_time__gte=now).order_by('start_time')

        return queryset.select_related('court', 'court__venue')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'upcoming')
        return context
