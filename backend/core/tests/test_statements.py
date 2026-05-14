from django.test import TestCase
from rest_framework.test import APIClient
from core.models import Event, Country, Statement, Event
from django.contrib.auth.models import User


class StatementAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            password="pass123",
            is_staff=True
        )
        self.event_ru = Event.objects.create(
            title="Russia-Ukraine Conflict",
            start_date="2022-02-24"
        )

        self.event_test = Event.objects.create(
            title="Test Event",
            start_date="2024-01-01"
        )
        self.client.force_authenticate(user=self.admin)
        self.country = Country.objects.create(
            name="India", isoa2_code="IN", lat=20.5, lng=78.9,
            isoa3_code='IND'
        )
        self.event = Event.objects.create(
            title="Test Event", start_date="2024-01-01"
        )

    # def test_get_statements(self):
    #     Statement.objects.create(
    #         country=self.country,
    #         event=self.event,
    #         text="Test statement",
    #         stance="neutral",
    #         publish_date="2022-02-24"
    #     )

    #     response = self.client.get(f'/api/events/{self.event.id}/statements/')

    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(len(response.data), 1)
