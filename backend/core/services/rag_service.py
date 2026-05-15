import os
from openai import OpenAI
from pgvector.django import CosineDistance
from core.models import Statement, StatementChunk
from core.services.embedding_service import get_query_embedding

nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=os.getenv("NVIDIA_NIM_API_KEY")
)

# ──────── CHATBOT: Filtered RAG ────────


def answer_question(query: str, country: str, event: str) -> str:
    """Full RAG pipeline for the AI chatbot."""

    # 1. RETRIEVE — embed question, search chunks filtered by country+event
    query_embedding = get_query_embedding(query)

    top_chunks = (
        StatementChunk.objects
        .filter(
            statement__country__name=country,
            statement__event__title=event
        )
        .annotate(distance=CosineDistance('embedding', query_embedding))
        .order_by('distance')           # closest first
        .select_related('statement')    # avoid N+1
        [:5]                            # top 5 most relevant chunks
    )

    if not top_chunks:
        return "No statements found for this country and event."

    # 2. AUGMENT — build context string
    context = "\n\n---\n\n".join([
        f"Source: {c.statement.id or 'Unknown'}\n{c.chunk_text}"
        for c in top_chunks
    ])

    # 3. GENERATE — call LLM with retrieved context
    system_prompt = f"""You are a geopolitical analysis assistant for GeoVoice.
Answer ONLY based on the official statements provided below.
Country: {country} | Event: {event}

Official Statements:
{context}

If the answer is not in the statements, say:
"This information is not available in the official statements."
Keep your answer concise and factual."""

    response = nvidia_client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",  # free NVIDIA NIM LLM
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": query}
        ],
        temperature=0.2,   # low = factual, consistent
        max_tokens=512
    )
    return response.choices[0].message.content
