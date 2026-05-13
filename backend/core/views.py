# core/views.py

from rest_framework import generics
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event, Statement, Country
from .serializers import EventSerializer, StatementSerializer, CountrySerializer

from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from .permissions import IsAdminOrReadOnly


# GET + POST
class EventListCreateView(generics.ListCreateAPIView):
    # queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return (
            Event.objects
            .annotate(total_statements=Count("statement"))
            .order_by("-total_statements")
        )


# GET + PATCH + DELETE
class EventDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminOrReadOnly]


# GET + POST
class CountryListCreateView(generics.ListCreateAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]


# GET + PATCH + DELETE
class CountryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    permission_classes = [IsAdminOrReadOnly]



# GET + POST
class StatementListCreateView(generics.ListCreateAPIView):
    queryset = Statement.objects.all()
    serializer_class = StatementSerializer
    permission_classes = [IsAdminOrReadOnly]


# GET + PATCH + DELETE
class StatementDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Statement.objects.all()
    serializer_class = StatementSerializer
    permission_classes = [IsAdminOrReadOnly]


# GET statements by event
class EventStatementsView(generics.ListAPIView):
    serializer_class = StatementSerializer
    permission_classes = [AllowAny]


    def get_queryset(self):
        return Statement.objects.filter(event_id=self.kwargs['pk'])\
            .annotate(total_statements=Count("statement"))\
            .order_by("-total_statements")

# GET statements by event + country
class EventCountryStatementsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, event_id, country_code):
        statements = (
            Statement.objects
            .filter(
                event_id=event_id,
                country__isoa3_code=country_code
            )
            .select_related("country")
            .order_by("-publish_date")
        )

        country = Country.objects.filter(
            isoa3_code=country_code
        ).first()

        if not country:
            return Response(
                {"detail": "Country not found"},
                status=404
            )

        return Response({
            "country": {
                "full_name": country.full_name,
                "country_name": country.name,
                "isoa2_code": country.isoa2_code,
                "isoa3_code": country.isoa3_code,
            },

            "statements": StatementSerializer(
                statements,
                many=True
            ).data
        })

# Heatmap
class EventHeatmapView(APIView):
    def get(self, request, pk):
        heatmap = Statement.objects.filter(event_id=pk)\
            .values(
                'country__name',
                'country__isoa3_code',
                'country__isoa2_code',
                'country__full_name',
                'country__lat',
                'country__lng'
            )\
            .annotate(statement_count=Count('id'))\
            .order_by('-statement_count')
        print("**heatmap",heatmap)
        return Response([
            {
                "country": i['country__name'],
                "isoa3_code": i['country__isoa3_code'],
                "isoa2_code": i['country__isoa2_code'],
                "full_name": i['country__full_name'],
                "statement_count": i['statement_count']
            }
            for i in heatmap
        ])
