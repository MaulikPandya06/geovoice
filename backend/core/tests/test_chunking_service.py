from django.test import TestCase
from core.services.chunking_service import chunk_text


class ChunkTextTest(TestCase):

    def test_short_text_returns_single_chunk(self):
        """Text shorter than chunk_size should return as one chunk."""
        text = " ".join(["word"] * 100)   # 100 words
        chunks = chunk_text(text, chunk_size=400, overlap=50)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_large_text_is_split_into_multiple_chunks(self):
        """900-word text with chunk_size=400 should produce 3 chunks."""
        text = " ".join(["word"] * 900)
        chunks = chunk_text(text, chunk_size=400, overlap=50)
        self.assertGreater(len(chunks), 1)

    def test_overlap_means_chunks_share_words(self):
        """Last words of chunk N should appear at start of chunk N+1."""
        text = " ".join([str(i) for i in range(500)])  # "0 1 2 3 ... 499"
        chunks = chunk_text(text, chunk_size=400, overlap=50)

        # Last 50 words of chunk 0 should equal first 50 words of chunk 1
        end_of_chunk_0   = chunks[0].split()[-50:]
        start_of_chunk_1 = chunks[1].split()[:50]
        self.assertEqual(end_of_chunk_0, start_of_chunk_1)

    def test_empty_text_returns_empty_list(self):
        chunks = chunk_text("")
        self.assertEqual(chunks, [])

    def test_chunk_size_respected(self):
        """No chunk should exceed chunk_size words."""
        text = " ".join(["word"] * 1000)
        chunks = chunk_text(text, chunk_size=400, overlap=50)
        for chunk in chunks:
            self.assertLessEqual(len(chunk.split()), 400)
