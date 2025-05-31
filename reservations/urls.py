from django.urls import path
from .views import (
    CourtAvailabilityView,
    ReservationCreateView,
    UserReservationListView,
)

app_name = 'reservations'

urlpatterns = [
    path('court/<int:court_pk>/availability/', CourtAvailabilityView.as_view(), name='court-availability'),
    path('court/<int:court_pk>/book/', ReservationCreateView.as_view(), name='reservation-create'),
    path('my-reservations/', UserReservationListView.as_view(), name='my-reservations'),
]
