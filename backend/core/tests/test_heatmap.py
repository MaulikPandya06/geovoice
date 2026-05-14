from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Event, Country, Statement
from django.contrib.auth.models import User


class HeatmapAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            password="pass123",
            is_staff=True
        )
        self.client.force_authenticate(user=self.admin)
        self.country = Country.objects.create(
            name="USA", isoa2_code="US", lat=37.0, lng=-95.0, isoa3_code='USA'
        )
        self.event = Event.objects.create(
            title="War", start_date="2024-01-01"
        )

    def test_heatmap(self):
        Statement.objects.create(
            country=self.country,
            event=self.event,
            text="Statement 1",
            stance="support",
            publish_date="2024-01-02"
        )

        Statement.objects.create(
            country=self.country,
            event=self.event,
            text="Statement 2",
            stance="support",
            publish_date="2024-01-03"
        )

        response = self.client.get(f'/api/events/{self.event.id}/heatmap/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['statement_count'], 2)
