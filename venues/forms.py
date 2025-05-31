from django import forms
from .models import Venue

class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'address', 'phone_number', 'description']
        # 'owner' field will be set automatically in the view
