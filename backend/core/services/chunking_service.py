# statements/services/chunking_service.py

def chunk_text(
    text: str,
    chunk_size: int = 400,
    overlap: int = 50,
) -> list[str]:
    """
    Split text into overlapping word-based chunks.

    Example with chunk_size=400, overlap=50:
      Chunk 0 → words 0   to 399
      Chunk 1 → words 350 to 749  (50-word overlap with chunk 0)
      Chunk 2 → words 700 to 1099 (50-word overlap with chunk 1)

    Overlap ensures context at boundaries isn't lost.
    """
    words = text.split()

    if not words:
        return []

    # If the whole text fits in one chunk, just return it as-is
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    step = chunk_size - overlap  # 350 — how far we move forward each iteration

    for i in range(0, len(words), step):
        chunk_words = words[i: i + chunk_size]

        # Skip tiny trailing chunks (less than 50 words = not useful)
        if len(chunk_words) < 50:
            break

        chunks.append(" ".join(chunk_words))

    return chunks
