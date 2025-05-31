from django.db import models
from venues.models import Venue

class CourtType(models.Model):
    name = models.CharField(max_length=100, unique=True) # Padel, Futbol5, Futbol7, Futbol11
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Court(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='courts')
    name = models.CharField(max_length=100) # e.g., "Main Padel Court", "Field A"
    court_type = models.ForeignKey(CourtType, on_delete=models.PROTECT, related_name='courts')
    description = models.TextField(blank=True, null=True)
    # photo = models.ImageField(upload_to='court_photos/', blank=True, null=True) # Optional
    is_active = models.BooleanField(default=True) # To temporarily disable a court
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.venue.name} - {self.name} ({self.court_type.name})"

class TurnDuration(models.Model):
    court = models.OneToOneField(Court, on_delete=models.CASCADE, related_name='turn_duration_setting')
    duration_minutes = models.PositiveIntegerField(default=60) # e.g., 60, 90, 120 minutes
    # We could also make this more flexible, e.g. multiple possible durations per court
    # For now, one fixed duration per court simplifies things.
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.court.name} - {self.duration_minutes} minutes"

    class Meta:
        verbose_name_plural = "Turn Durations"
