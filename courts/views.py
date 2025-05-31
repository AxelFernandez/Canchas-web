from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from venues.models import Venue # Need this to associate courts with venues
from .models import Court, CourtType, TurnDuration
from reservations.models import Reservation
from .forms import CourtForm, TurnDurationForm
from venues.views import VenueOwnerRequiredMixin # Re-use the mixin

class CourtListView(LoginRequiredMixin, VenueOwnerRequiredMixin, ListView):
    model = Court
    template_name = 'courts/court_list.html' # To be created
    context_object_name = 'courts'

    def get_queryset(self):
        # Ensure we only list courts for the current venue owner's venues
        # This view might be better if it's for a specific venue.
        # For now, let's list all courts from all venues of the owner.
        # return Court.objects.filter(venue__owner=self.request.user) # Original broader query
        # Refined query based on URL:
        self.venue = get_object_or_404(Venue, pk=self.kwargs['venue_pk'], owner=self.request.user)
        return Court.objects.filter(venue=self.venue)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # If we want to add a court, we need a venue.
        # This view is not ideal for adding courts without a venue context.
        # Let's refine this: this view should be for a specific venue.
        # The URL will provide venue_pk.
        # self.venue object is already set in get_queryset if using the refined query there.
        # If not, it needs to be set here. For clarity, let's ensure it's available.
        if not hasattr(self, 'venue'): # Ensure venue is set if not by get_queryset
             self.venue = get_object_or_404(Venue, pk=self.kwargs['venue_pk'], owner=self.request.user)
        context['venue'] = self.venue
        # context['courts'] = Court.objects.filter(venue=self.venue) # This is handled by get_queryset
        return context

class CourtCreateView(LoginRequiredMixin, VenueOwnerRequiredMixin, CreateView):
    model = Court
    form_class = CourtForm
    template_name = 'courts/court_form.html' # To be created

    def dispatch(self, request, *args, **kwargs):
        self.venue = get_object_or_404(Venue, pk=self.kwargs['venue_pk'], owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # kwargs['venue_owner'] = self.request.user # If needed by form
        return kwargs

    def form_valid(self, form):
        form.instance.venue = self.venue
        court = form.save()
        # Default TurnDuration - can be edited later
        TurnDuration.objects.create(court=court, duration_minutes=60)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venue'] = self.venue
        return context

    def get_success_url(self):
        return reverse('courts:court-list', kwargs={'venue_pk': self.venue.pk})


class CourtDetailView(LoginRequiredMixin, VenueOwnerRequiredMixin, DetailView):
    model = Court
    template_name = 'courts/court_detail.html' # To be created
    context_object_name = 'court'

    def get_queryset(self):
        # Ensure user owns the venue of the court
        return Court.objects.filter(venue__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Also pass the TurnDurationForm for editing turn duration
        turn_duration, created = TurnDuration.objects.get_or_create(court=self.object)
        context['turn_duration_form'] = TurnDurationForm(instance=turn_duration)
        context['upcoming_reservations'] = Reservation.objects.filter(
            court=self.object,
            start_time__gte=timezone.now()
        ).order_by('start_time')
        return context

class CourtUpdateView(LoginRequiredMixin, VenueOwnerRequiredMixin, UpdateView):
    model = Court
    form_class = CourtForm
    template_name = 'courts/court_form.html'

    def get_queryset(self):
        return Court.objects.filter(venue__owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['venue'] = self.object.venue
        return context

    def get_success_url(self):
        return reverse('courts:court-detail', kwargs={'pk': self.object.pk})


class CourtDeleteView(LoginRequiredMixin, VenueOwnerRequiredMixin, DeleteView):
    model = Court
    template_name = 'courts/court_confirm_delete.html' # To be created
    context_object_name = 'court'

    def get_queryset(self):
        return Court.objects.filter(venue__owner=self.request.user)

    def get_success_url(self):
        # Redirect to the list of courts for the venue from which the court was deleted
        return reverse('courts:court-list', kwargs={'venue_pk': self.object.venue.pk})


class TurnDurationUpdateView(LoginRequiredMixin, VenueOwnerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        court = get_object_or_404(Court, pk=self.kwargs['court_pk'], venue__owner=request.user)
        turn_duration, created = TurnDuration.objects.get_or_create(court=court)
        form = TurnDurationForm(request.POST, instance=turn_duration)
        if form.is_valid():
            form.save()
        return redirect('courts:court-detail', pk=court.pk)
