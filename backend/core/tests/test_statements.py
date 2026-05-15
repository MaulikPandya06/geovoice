from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient

from core.models import Country, Event


class StatementAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="admin",
            password="pass123",
            is_staff=True,
        )

        self.event_ru = Event.objects.create(
            title="Russia-Ukraine Conflict",
            start_date="2022-02-24",
        )

        self.event_test = Event.objects.create(
            title="Test Event",
            start_date="2024-01-01",
        )

        self.client.force_authenticate(user=self.admin)

        self.country = Country.objects.create(
            name="India",
            isoa2_code="IN",
            lat=20.5,
            lng=78.9,
            isoa3_code="IND",
        )

        self.event = Event.objects.create(
            title="Test Event",
            start_date="2024-01-01",
        )
