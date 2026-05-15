from unittest.mock import MagicMock, patch

from django.test import TestCase

from core.services.embedding_service import (
    get_passage_embedding,
    get_query_embedding,
)

# Fake 1024-dim vector returned by NVIDIA API
FAKE_EMBEDDING = [0.1] * 1024


class EmbeddingServiceTest(TestCase):

    @patch("core.services.embedding_service.nvidia_client")
    def test_get_query_embedding_returns_list_of_floats(
        self,
        mock_client,
    ):
        """get_query_embedding() should return 1024 floats."""

        # Mock:
        # nvidia_client.embeddings.create(...).data[0].embedding
        mock_data = MagicMock()
        mock_data.embedding = FAKE_EMBEDDING

        mock_client.embeddings.create.return_value.data = [
            mock_data
        ]

        result = get_query_embedding(
            "What is Germany's stance?"
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1024)
        self.assertEqual(result, FAKE_EMBEDDING)

    @patch("core.services.embedding_service.nvidia_client")
    def test_get_passage_embedding_returns_list_of_floats(
        self,
        mock_client,
    ):
        """get_passage_embedding() should return 1024 floats."""
        mock_data = MagicMock()
        mock_data.embedding = FAKE_EMBEDDING

        mock_client.embeddings.create.return_value.data = [
            mock_data
        ]

        result = get_passage_embedding(
            "Germany strongly supports Ukraine."
        )

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1024)

    @patch("core.services.embedding_service.nvidia_client")
    def test_query_embedding_uses_query_input_type(
        self,
        mock_client,
    ):
        """Query embedding should use input_type='query'."""
        mock_data = MagicMock()
        mock_data.embedding = FAKE_EMBEDDING

        mock_client.embeddings.create.return_value.data = [
            mock_data
        ]

        get_query_embedding("test question")

        # Inspect actual call made to the mock
        call_kwargs = (
            mock_client.embeddings.create.call_args
        )

        self.assertEqual(
            call_kwargs.kwargs["extra_body"]["input_type"],
            "query",
        )

    @patch("core.services.embedding_service.nvidia_client")
    def test_passage_embedding_uses_passage_input_type(
        self,
        mock_client,
    ):
        """Passage embedding should use input_type='passage'."""
        mock_data = MagicMock()
        mock_data.embedding = FAKE_EMBEDDING

        mock_client.embeddings.create.return_value.data = [
            mock_data
        ]

        get_passage_embedding("some document text")

        call_kwargs = (
            mock_client.embeddings.create.call_args
        )

        self.assertEqual(
            call_kwargs.kwargs["extra_body"]["input_type"],
            "passage",
        )
