from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    is_venue_owner = forms.BooleanField(required=False, label="Register as Venue Owner")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name', 'is_venue_owner',)

class CustomAuthenticationForm(AuthenticationForm):
    pass
