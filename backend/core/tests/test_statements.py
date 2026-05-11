from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Event, Country, Statement
from django.contrib.auth.models import User


class StatementAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            password="pass123",
            is_staff=True
        )
        self.client.force_authenticate(user=self.admin)
        self.country = Country.objects.create(
            name="India", code="IN", lat=20.5, lng=78.9
        )
        self.event = Event.objects.create(
            title="Test Event", date="2024-01-01"
        )

    def test_get_statements(self):
        Statement.objects.create(
            country=self.country,
            event=self.event,
            text="Test statement",
            stance="neutral",
            date="2024-01-02"
        )

        response = self.client.get(f'/api/events/{self.event.id}/statements/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
