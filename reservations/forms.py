from django import forms
from .models import Reservation
from django.core.exceptions import ValidationError
import datetime # Keep for now, but prefer timezone from django.utils
from django.utils import timezone # Preferred for timezone-aware operations


class ReservationForm(forms.ModelForm):
    # The view will pass initial data for court and start_time
    # User will be set from request.user
    # For now, we only need notes from the user, if any.
    # Court and start_time will be hidden inputs or set in the view.

    # We might need to select a date and then a time slot based on availability.
    # For this iteration, let's assume the user clicks a specific slot (start_time is known).

    start_time = forms.DateTimeField(widget=forms.HiddenInput()) # Will be pre-filled
    # Use CharField for court_id to avoid potential issues with IntegerField widget if value is not strictly int
    court_id = forms.CharField(widget=forms.HiddenInput()) # Will be pre-filled, changed to CharField

    class Meta:
        model = Reservation
        fields = ['notes', 'start_time', 'court_id'] # User and end_time are set in the view/model

    def __init__(self, *args, **kwargs):
        self.court = kwargs.pop('court', None)
        super().__init__(*args, **kwargs)
        if 'court_id' in self.fields and self.court:
             self.fields['court_id'].initial = str(self.court.pk) # Ensure it's a string for CharField


    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        # Ensure start_time is timezone-aware for comparison
        if timezone.is_naive(start_time):
            start_time = timezone.make_aware(start_time, timezone.get_default_timezone())

        if start_time < timezone.now():
            raise ValidationError("Cannot book a reservation in the past.")
        # Add more validation if needed, e.g., within venue operating hours
        return start_time

    def clean_court_id(self): # Add specific cleaner for court_id
        court_id_str = self.cleaned_data.get('court_id')
        try:
            return int(court_id_str)
        except (ValueError, TypeError):
            raise ValidationError("Invalid Court ID.")


    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        # court_id is now cleaned by clean_court_id
        court_id = cleaned_data.get('court_id')


        if not self.court and court_id: # If court object wasn't passed, try to get it
            from courts.models import Court
            try:
                self.court = Court.objects.get(pk=court_id)
            except Court.DoesNotExist:
                raise ValidationError("Selected court does not exist.")
            except ValueError: # If court_id is not a valid int after clean_court_id (e.g. None)
                raise ValidationError("Invalid Court ID format.")


        if self.court and start_time:
            # Ensure start_time is timezone-aware for calculations
            if timezone.is_naive(start_time):
                 start_time = timezone.make_aware(start_time, timezone.get_default_timezone())

            # Calculate end_time
            from datetime import timedelta # Keep this import local as it's specific
            duration = self.court.turn_duration_setting.duration_minutes
            end_time = start_time + timedelta(minutes=duration)

            # Check for overlapping reservations
            # Exclude self if this form is used for updating an existing reservation
            queryset = Reservation.objects.filter(
                court=self.court,
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            if self.instance and self.instance.pk: # If updating an existing reservation
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise ValidationError("This time slot is no longer available. Please select another.")
        return cleaned_data
