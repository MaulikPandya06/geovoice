from django.test import TestCase
from unittest.mock import patch
from core.models import Statement, StatementChunk, Country, Event

FAKE_EMBEDDING = [0.1] * 1024


class StatementModelTest(TestCase):

    def setUp(self):
        """Create reusable test data before each test."""
        self.country_germany = Country.objects.create(name="Germany", isoa3_code='GRM', isoa2_code='GR')
        self.country_france  = Country.objects.create(name="France", isoa3_code='FRN', isoa2_code='FR')

        self.event_ru = Event.objects.create(
            title="Russia-Ukraine Conflict",
            description="War event",
            start_date="2022-02-24"
        )

        self.event_test = Event.objects.create(
            title="Test Event",
            description="Test",
            start_date="2024-01-01"
        )

    def test_statement_creation(self):
        s = Statement.objects.create(
            country=self.country_germany,   # pass the object, not a string
            event=self.event_ru,
            text="Germany supports Ukraine.",
            publish_date="2022-02-24"
        )
        self.assertEqual(s.country, self.country_germany)
        self.assertEqual(s.event, self.event_ru)
        self.assertIsNotNone(s.pk)

    def test_statement_str(self):
        s = Statement(
            country=self.country_france,    # object, not string
            event=self.event_test,
            text="test",
            publish_date="2022-02-24"
        )
        self.assertIn("France", str(s))

    def test_statementchunk_reverse_relation(self):
        test_event = Event.objects.create(
            title="Test",
            start_date="2024-01-01"
        )

        s = Statement.objects.create(
            country=self.country_germany,
            event=self.event_test,
            text="Some text here.",
            publish_date="2022-02-24"
        )
        StatementChunk.objects.create(
            statement=s, chunk_index=0,
            chunk_text="Some text here.", embedding=FAKE_EMBEDDING
        )
        self.assertTrue(s.chunks.exists())
        self.assertIsNotNone(s.chunks.first())


class StatementSignalTest(TestCase):

    def setUp(self):
        self.country_france = Country.objects.create(name="France", isoa3_code='FRN', isoa2_code='FR') # code are not real in all testing files
        self.country_uk     = Country.objects.create(name="UK", isoa3_code='UNK', isoa2_code='UK')
        self.country_italy  = Country.objects.create(name="Italy", isoa3_code='ITL', isoa2_code='IL')

    @patch('core.signals.embed_statement')
    def test_signal_calls_embed_statement_on_create(self, mock_embed):
        event_ru = Event.objects.create(
            title="Russia-Ukraine Conflict",
            start_date="2022-02-24"
        )
        Statement.objects.create(
            country=self.country_france,
            event=event_ru,
            text="France condemns the invasion.",
            publish_date="2022-02-24"
        )
        mock_embed.assert_called_once()

    @patch('core.signals.embed_statement')
    def test_signal_passes_correct_statement_to_embed(self, mock_embed):
        event_test = Event.objects.create(
            title="Russia-Ukraine Conflict",
            start_date="2022-02-24"
        )
        s = Statement.objects.create(
            country=self.country_uk,
            event=event_test,
            text="The UK stands firm.",
            publish_date="2022-02-24"
        )
        called_with_statement = mock_embed.call_args[0][0]
        self.assertEqual(called_with_statement.pk, s.pk)

    @patch('core.signals.embed_statement')
    def test_signal_does_not_fire_on_update(self, mock_embed):
        event_test = Event.objects.create(
            title="Russia-Ukraine Conflict",
            start_date="2022-02-24"
        )
        s = Statement.objects.create(
            country=self.country_italy,
            event=event_test,
            text="Original text.",
            publish_date="2022-02-24"
        )
        mock_embed.reset_mock()

        s.source = "Updated Source"
        s.save()

        mock_embed.assert_not_called()
