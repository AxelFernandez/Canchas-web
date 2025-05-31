from django import forms
from .models import Court, CourtType, TurnDuration

class CourtForm(forms.ModelForm):
    # Venue will be set in the view or passed to the form
    class Meta:
        model = Court
        fields = ['name', 'court_type', 'description', 'is_active']

    def __init__(self, *args, **kwargs):
        # venue_owner = kwargs.pop('venue_owner', None) # Not strictly needed if views handle filtering
        super().__init__(*args, **kwargs)
        self.fields['court_type'].queryset = CourtType.objects.all()
        self.fields['court_type'].empty_label = None # Require a selection


class TurnDurationForm(forms.ModelForm):
    class Meta:
        model = TurnDuration
        fields = ['duration_minutes']
