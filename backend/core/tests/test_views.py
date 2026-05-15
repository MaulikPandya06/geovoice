import json
from unittest.mock import patch

from django.test import Client, TestCase

from core.models import (
    Country,
    Event,
    Statement,
    StatementChunk,
)

FAKE_EMBEDDING = [0.1] * 1024


class ChatbotViewTest(TestCase):

    def setUp(self):
        self.client = Client()

        country_germany = Country.objects.create(
            name="Germany",
            isoa3_code="GRM",
            isoa2_code="GM",
        )

        event_ru = Event.objects.create(
            title="Russia-Ukraine Conflict",
            start_date="2022-02-24",
        )

        statement = Statement.objects.create(
            country=country_germany,
            event=event_ru,
            text="Germany supports Ukraine.",
            publish_date="2022-02-24",
        )

        StatementChunk.objects.create(
            statement=statement,
            chunk_index=0,
            chunk_text="Germany supports Ukraine.",
            embedding=FAKE_EMBEDDING,
        )

    @patch(
        "core.views.answer_question",
        return_value="Germany supports Ukraine.",
    )
    def test_chatbot_returns_200_with_valid_data(
        self,
        mock_answer,
    ):
        response = self.client.post(
            "/api/chatbot/",
            data=json.dumps(
                {
                    "question": "What is Germany's stance?",
                    "country": "Germany",
                    "event": "Russia-Ukraine Conflict",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        self.assertIn("answer", data)

        self.assertEqual(
            data["answer"],
            "Germany supports Ukraine.",
        )

    @patch("core.views.answer_question")
    def test_chatbot_returns_400_when_fields_missing(
        self,
        mock_answer,
    ):
        """Missing event field should return 400."""

        response = self.client.post(
            "/api/chatbot/",
            data=json.dumps(
                {
                    "question": "What is Germany's stance?",
                    "country": "Germany",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        data = json.loads(response.content)

        self.assertIn("error", data)

        # answer_question should never be called
        mock_answer.assert_not_called()

    @patch("core.views.answer_question")
    def test_chatbot_returns_400_for_empty_question(
        self,
        mock_answer,
    ):
        response = self.client.post(
            "/api/chatbot/",
            data=json.dumps(
                {
                    "question": "",
                    "country": "Germany",
                    "event": "Russia-Ukraine Conflict",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

    def test_chatbot_returns_405_for_get_request(self):
        """GET request should not be allowed."""

        response = self.client.get("/api/chatbot/")

        self.assertEqual(response.status_code, 405)


class SummaryViewTest(TestCase):

    @patch(
        "core.views.generate_summary",
        return_value="Germany is a strong supporter.",
    )
    def test_summary_returns_200_with_valid_data(
        self,
        mock_summary,
    ):
        response = self.client.post(
            "/api/summary/",
            data=json.dumps(
                {
                    "country": "Germany",
                    "event": "Russia-Ukraine Conflict",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.content)

        self.assertIn("summary", data)

        self.assertEqual(
            data["summary"],
            "Germany is a strong supporter.",
        )

    @patch("core.views.generate_summary")
    def test_summary_returns_400_when_country_missing(
        self,
        mock_summary,
    ):
        response = self.client.post(
            "/api/summary/",
            data=json.dumps(
                {
                    "event": "Russia-Ukraine Conflict",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)

        mock_summary.assert_not_called()

    def test_summary_returns_405_for_get_request(self):
        response = self.client.get("/api/summary/")

        self.assertEqual(response.status_code, 405)
