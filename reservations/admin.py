from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('court', 'user', 'start_time', 'end_time', 'is_confirmed', 'created_at')
    list_filter = ('is_confirmed', 'court__venue__name', 'court__court_type', 'start_time')
    search_fields = ('user__username', 'court__name', 'court__venue__name')
    raw_id_fields = ('user', 'court') # For easier selection
    date_hierarchy = 'start_time'
