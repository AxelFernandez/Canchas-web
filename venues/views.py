from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Venue
from .forms import VenueForm
from courts.models import Court # Added for VenuePublicDetailView

class VenueOwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_venue_owner

class VenueListView(LoginRequiredMixin, VenueOwnerRequiredMixin, ListView):
    model = Venue
    template_name = 'venues/venue_list.html'
    context_object_name = 'venues'

    def get_queryset(self):
        # Only list venues owned by the current user
        return Venue.objects.filter(owner=self.request.user)

class VenueCreateView(LoginRequiredMixin, VenueOwnerRequiredMixin, CreateView):
    model = Venue
    form_class = VenueForm
    template_name = 'venues/venue_form.html'
    success_url = reverse_lazy('venues:venue-list') # Redirect to venue list after creation

    def form_valid(self, form):
        form.instance.owner = self.request.user # Set the owner to the current user
        return super().form_valid(form)

class VenueUpdateView(LoginRequiredMixin, VenueOwnerRequiredMixin, UpdateView):
    model = Venue
    form_class = VenueForm
    template_name = 'venues/venue_form.html'
    success_url = reverse_lazy('venues:venue-list')

    def get_queryset(self):
        # Ensure users can only update their own venues
        return Venue.objects.filter(owner=self.request.user)

class VenueDeleteView(LoginRequiredMixin, VenueOwnerRequiredMixin, DeleteView):
    model = Venue
    template_name = 'venues/venue_confirm_delete.html'
    success_url = reverse_lazy('venues:venue-list')
    context_object_name = 'venue'

    def get_queryset(self):
        # Ensure users can only delete their own venues
        return Venue.objects.filter(owner=self.request.user)

class VenuePublicListView(ListView):
    model = Venue
    template_name = 'venues/venue_public_list.html' # To be created
    context_object_name = 'venues'
    queryset = Venue.objects.all() # Or some filtering for active/approved venues

class VenuePublicDetailView(DetailView):
    model = Venue
    template_name = 'venues/venue_public_detail.html' # To be created
    context_object_name = 'venue'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get active courts for this venue
        context['courts'] = Court.objects.filter(venue=self.object, is_active=True)
        return context
