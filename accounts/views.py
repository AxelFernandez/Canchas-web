from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm, CustomAuthenticationForm # Ensure this import is correct

# Using Django's built-in LoginView and LogoutView for simplicity for now
from django.contrib.auth.views import LoginView, LogoutView

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login') # Redirect to login page after successful registration
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_venue_owner = form.cleaned_data.get('is_venue_owner', False)
        user.save()
        # login(self.request, user) # Optionally log the user in directly
        return super().form_valid(form)

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'registration/login.html'
    # success_url will be handled by Django's default (LOGIN_REDIRECT_URL in settings)

# No custom view needed for logout if using Django's LogoutView directly in urls.py
