from django.contrib import admin
from .models import CourtType, Court, TurnDuration

@admin.register(CourtType)
class CourtTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Court)
class CourtAdmin(admin.ModelAdmin):
    list_display = ('name', 'venue', 'court_type', 'is_active', 'created_at')
    list_filter = ('court_type', 'is_active', 'venue__name')
    search_fields = ('name', 'venue__name', 'court_type__name')
    raw_id_fields = ('venue',) # For easier venue selection

@admin.register(TurnDuration)
class TurnDurationAdmin(admin.ModelAdmin):
    list_display = ('court', 'duration_minutes', 'updated_at')
    list_filter = ('duration_minutes',)
    search_fields = ('court__name',)
    raw_id_fields = ('court',)
