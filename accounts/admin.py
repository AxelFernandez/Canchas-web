from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_venue_owner']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_venue_owner',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_venue_owner',)}),
    )

admin.site.register(User, CustomUserAdmin)
