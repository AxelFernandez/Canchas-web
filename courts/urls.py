from django.urls import path
from .views import (
    CourtListView,
    CourtCreateView,
    CourtDetailView,
    CourtUpdateView,
    CourtDeleteView,
    TurnDurationUpdateView,
)

app_name = 'courts'

urlpatterns = [
    # List courts for a specific venue
    path('venue/<int:venue_pk>/courts/', CourtListView.as_view(), name='court-list'),
    # Create a court for a specific venue
    path('venue/<int:venue_pk>/courts/create/', CourtCreateView.as_view(), name='court-create'),
    # Court specific actions
    path('<int:pk>/', CourtDetailView.as_view(), name='court-detail'),
    path('<int:pk>/update/', CourtUpdateView.as_view(), name='court-update'),
    path('<int:pk>/delete/', CourtDeleteView.as_view(), name='court-delete'),
    # Update turn duration for a specific court
    path('<int:court_pk>/turn-duration/update/', TurnDurationUpdateView.as_view(), name='turn-duration-update'),
]
