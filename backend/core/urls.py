# core/urls.py

from django.urls import path

from .views import (
    ChatbotView,
    CountryDetailView,
    CountryEventSummaryView,
    CountryListCreateView,
    EventCountryStatementsView,
    EventDetailView,
    EventHeatmapView,
    EventListCreateView,
    EventStatementsView,
    StatementDetailView,
    StatementListCreateView,
)

urlpatterns = [
    # Events
    path("events/", EventListCreateView.as_view()),
    path("events/<int:pk>/", EventDetailView.as_view()),

    # Countries
    path("countries/", CountryListCreateView.as_view()),
    path("countries/<int:pk>/", CountryDetailView.as_view()),
    path(
        (
            "events/<int:event_id>/countries/"
            "<str:country_code>/statements/"
        ),
        EventCountryStatementsView.as_view(),
    ),

    # Statements
    path("statements/", StatementListCreateView.as_view()),
    path("statements/<int:pk>/", StatementDetailView.as_view()),

    # Special
    path(
        "events/<int:pk>/statements/",
        EventStatementsView.as_view(),
    ),
    path(
        "events/<int:pk>/heatmap/",
        EventHeatmapView.as_view(),
    ),

    # AI Endpoints
    path(
        "chatbot/",
        ChatbotView.as_view(),
        name="chatbot",
    ),
    path(
        "summary/",
        CountryEventSummaryView.as_view(),
        name="summary",
    ),
]