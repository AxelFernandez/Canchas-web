from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_venue_owner = models.BooleanField(default=False)
    # Add any other custom fields for users here
    # For example: phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username
