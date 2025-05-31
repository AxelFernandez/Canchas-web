from django.db import models
from django.conf import settings
from courts.models import Court

class Reservation(models.Model):
    court = models.ForeignKey(Court, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField() # This will be calculated based on court's TurnDuration
    notes = models.TextField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=True) # Or add a confirmation workflow
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Reservation for {self.court.name} by {self.user.username} from {self.start_time.strftime('%Y-%m-%d %H:%M')} to {self.end_time.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        if not self.end_time and self.court and self.start_time:
            # Calculate end_time based on court's turn duration
            from datetime import timedelta
            duration = self.court.turn_duration_setting.duration_minutes
            self.end_time = self.start_time + timedelta(minutes=duration)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['start_time']
        unique_together = ('court', 'start_time') # Prevent double booking for the same slot
