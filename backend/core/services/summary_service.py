import os
from openai import OpenAI

from core.models import (
    Statement,
    CountryEventSummary
)

def get_nvidia_client():

    nvidia_api_key = os.getenv(
        "NVIDIA_NIM_API_KEY"
    )

    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=nvidia_api_key,
    )

# Approx safe size for Llama 3.1 prompt batching
MAX_CHARS_PER_BATCH = 12000


def call_llm_summary(prompt: str) -> str:
    """
    Single reusable summarization call.
    """

    nvidia_client = get_nvidia_client()
    response = nvidia_client.chat.completions.create(
        model="meta/llama-3.1-8b-instruct",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an elite geopolitical intelligence analyst.\n\n"

                    "Your task is to analyze official government statements "
                    "and produce a highly concise strategic briefing.\n\n"

                    "Focus on:\n"
                    "- diplomatic stance\n"
                    "- military posture\n"
                    "- sanctions/economic actions\n"
                    "- alliances and partnerships\n"
                    "- escalation or de-escalation tone\n"
                    "- humanitarian concerns\n"
                    "- recurring strategic themes\n\n"

                    "Rules:\n"
                    "- Output MUST be under 100 words.\n"
                    "- Be factual.\n"
                    "- Avoid repetition.\n"
                    "- Avoid generic wording.\n"
                    "- Write like an intelligence briefing.\n"
                    "- Do not mention missing information.\n"
                    "- No bullet points.\n"
                    "- Single concise paragraph."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=180
    )

    return response.choices[0].message.content.strip()


def split_into_batches(texts, max_chars=MAX_CHARS_PER_BATCH):
    """
    Group statement texts into safe-size batches.
    """

    batches = []
    current_batch = []
    current_size = 0

    for text in texts:

        text_size = len(text)

        if current_size + text_size > max_chars:
            batches.append(current_batch)
            current_batch = [text]
            current_size = text_size

        else:
            current_batch.append(text)
            current_size += text_size

    if current_batch:
        batches.append(current_batch)

    return batches


def regenerate_country_event_summary(country, event):
    """
    Hierarchical AI summarization pipeline.
    """

    statements = (
        Statement.objects
        .filter(
            country=country,
            event=event
        )
        .order_by('-publish_date')
    )

    if not statements.exists():
        return None

    # Step 1 — Prepare raw texts
    statement_texts = [
        s.text.strip()
        for s in statements
        if s.text
    ]

    # Step 2 — Split into batches
    batches = split_into_batches(statement_texts)

    partial_summaries = []

    # Step 3 — Summarize each batch
    for idx, batch in enumerate(batches):

        combined_text = "\n\n".join(batch)

        batch_prompt = (
            f"Official statements batch {idx + 1}:\n\n"
            f"{combined_text}"
        )

        partial_summary = call_llm_summary(batch_prompt)

        partial_summaries.append(partial_summary)

    # Step 4 — Final synthesis summary
    combined_partial_summaries = "\n\n".join(partial_summaries)

    final_prompt = (
        f"Country: {country.name}\n"
        f"Event: {event.title}\n\n"
        f"Partial intelligence summaries:\n\n"
        f"{combined_partial_summaries}\n\n"
        "Create the final strategic assessment."
    )

    final_summary = call_llm_summary(final_prompt)

    # Step 5 — Save
    summary_obj, _ = CountryEventSummary.objects.update_or_create(
        country=country,
        event=event,
        defaults={
            "summary": final_summary,
            "statement_count": statements.count()
        }
    )

    return summary_obj
