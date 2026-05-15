from unittest.mock import MagicMock, patch

from django.test import TestCase

from core.models import Country, Event, Statement, StatementChunk
from core.services.rag_service import (
    answer_question,
)

FAKE_EMBEDDING = [0.1] * 1024


class AnswerQuestionTest(TestCase):

    def setUp(self):
        """Create test data in the DB before each test."""
        self.country_germany = Country.objects.create(
            name="Germany",
            isoa3_code="GRM",
            isoa2_code="GM",
        )

        self.event_ru = Event.objects.create(
            title="Russia-Ukraine Conflict",
            start_date="2022-02-24",
        )

        self.statement = Statement.objects.create(
            country=self.country_germany,
            event=self.event_ru,
            text=(
                "Germany supports Ukraine with military "
                "and financial aid."
            ),
            publish_date="2022-02-24",
        )

        StatementChunk.objects.create(
            statement=self.statement,
            chunk_index=0,
            chunk_text=(
                "Germany supports Ukraine with military "
                "and financial aid."
            ),
            embedding=FAKE_EMBEDDING,
        )

    @patch("core.services.rag_service.nvidia_client")
    @patch("core.services.rag_service.get_query_embedding")
    def test_answer_question_returns_string(
        self,
        mock_embed,
        mock_llm,
    ):
        """answer_question() should return a non-empty string."""
        mock_embed.return_value = FAKE_EMBEDDING

        # Mock the LLM response
        mock_choice = MagicMock()
        mock_choice.message.content = (
            "Germany has provided military aid to Ukraine."
        )
        mock_llm.chat.completions.create.return_value.choices = [
            mock_choice
        ]

        result = answer_question(
            query="What aid has Germany given?",
            country=self.country_germany,
            event=self.event_ru,
        )

        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        self.assertEqual(
            result,
            "Germany has provided military aid to Ukraine.",
        )

    @patch("core.services.rag_service.nvidia_client")
    @patch("core.services.rag_service.get_query_embedding")
    def test_answer_question_no_statements_returns_fallback(
        self,
        mock_embed,
        mock_llm,
    ):
        """Return fallback message if no chunks exist."""
        mock_embed.return_value = FAKE_EMBEDDING

        result = answer_question(
            query="Some question",
            country="NonExistentCountry",
            event="NonExistentEvent",
        )

        self.assertIn("No statements found", result)

        # LLM should NOT be called if there's no context
        mock_llm.chat.completions.create.assert_not_called()

    @patch("core.services.rag_service.nvidia_client")
    @patch("core.services.rag_service.get_query_embedding")
    def test_answer_question_sends_correct_country_event_to_llm(
        self,
        mock_embed,
        mock_llm,
    ):
        """LLM system prompt should contain country and event."""
        mock_embed.return_value = FAKE_EMBEDDING

        mock_choice = MagicMock()
        mock_choice.message.content = "Some answer."

        mock_llm.chat.completions.create.return_value.choices = [
            mock_choice
        ]

        answer_question(
            query="test?",
            country=self.country_germany,
            event=self.event_ru,
        )

        # Inspect messages sent to the LLM
        call_kwargs = (
            mock_llm.chat.completions.create.call_args.kwargs
        )

        system_message = call_kwargs["messages"][0]["content"]

        self.assertIn("Germany", system_message)
        self.assertIn(
            "Russia-Ukraine Conflict",
            system_message,
        )


class GenerateSummaryTest(TestCase):

    def setUp(self):
        self.country_germany = Country.objects.create(
            name="Germany",
            isoa3_code="GRM",
            isoa2_code="GM",
        )

        self.event_ru = Event.objects.create(
            title="Russia-Ukraine Conflict",
            start_date="2022-02-24",
        )

        Statement.objects.create(
            country=self.country_germany,
            event=self.event_ru,
            text="Germany has pledged €1 billion in military aid.",
            publish_date="2022-02-24",
        )

    @patch("core.services.rag_service.nvidia_client")
    def test_generate_summary_returns_string(self, mock_llm):
        """generate_summary() should return a non-empty string."""
        mock_choice = MagicMock()

        mock_choice.message.content = (
            "Germany has been a strong supporter of Ukraine."
        )

        mock_llm.chat.completions.create.return_value.choices = [
            mock_choice
        ]

        result = generate_summary(
            country=self.country_germany,
            event=self.event_ru,
        )

        self.assertIsInstance(result, str)

        self.assertEqual(
            result,
            "Germany has been a strong supporter of Ukraine.",
        )

    @patch("core.services.rag_service.nvidia_client")
    def test_generate_summary_no_statements_returns_fallback(
        self,
        mock_llm,
    ):
        """Return fallback message without calling LLM."""
        event_test = Event.objects.create(
            title="Test",
            start_date="2022-02-24",
        )

        country_test = Country.objects.create(
            name="India",
            isoa2_code="IN",
            lat=20.5,
            lng=78.9,
            isoa3_code="IND",
        )

        result = generate_summary(
            country=country_test,
            event=event_test,
        )

        self.assertIn("No statements found", result)

        mock_llm.chat.completions.create.assert_not_called()
