from django.urls import path
from .views import (
    VenueListView,
    VenueCreateView,
    VenueUpdateView,
    VenueDeleteView,
    VenuePublicListView,
    VenuePublicDetailView
)

app_name = 'venues' # Namespace for URLs

urlpatterns = [
    path('', VenueListView.as_view(), name='venue-list'),
    path('create/', VenueCreateView.as_view(), name='venue-create'),
    path('<int:pk>/update/', VenueUpdateView.as_view(), name='venue-update'),
    path('<int:pk>/delete/', VenueDeleteView.as_view(), name='venue-delete'),
    # Public views
    path('public/', VenuePublicListView.as_view(), name='venue-public-list'),
    path('public/<int:pk>/', VenuePublicDetailView.as_view(), name='venue-public-detail'),
]
