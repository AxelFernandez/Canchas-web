from django.contrib import admin
from .models import Venue

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'phone_number', 'created_at')
    list_filter = ('owner', 'created_at')
    search_fields = ('name', 'address', 'owner__username')
    raw_id_fields = ('owner',) # For easier owner selection
