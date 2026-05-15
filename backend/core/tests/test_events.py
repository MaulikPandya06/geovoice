from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User


class EventCRUDTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin",
            password="pass123",
            is_staff=True
        )
        self.client.force_authenticate(self.admin)

    def test_create_event(self):
        response = self.client.post('/api/events/', {
            "title": "New Event",
            "start_date": "2024-01-01"
        })

        self.assertEqual(response.status_code, 201)

    def test_update_event(self):
        res = self.client.post('/api/events/', {
            "title": "Old",
            "start_date": "2024-01-01"
        })
        event_id = res.data['id']

        response = self.client.patch(f'/api/events/{event_id}/', {
            "title": "Updated"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], "Updated")

    def test_delete_event(self):
        res = self.client.post('/api/events/', {
            "title": "Delete Me",
            "start_date": "2024-01-01"
        })

        event_id = res.data['id']

        response = self.client.delete(f'/api/events/{event_id}/')

        self.assertEqual(response.status_code, 204)
