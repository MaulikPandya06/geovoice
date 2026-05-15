import hashlib
import json
import logging
import os
from datetime import datetime
from time import sleep

import redis
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from elasticsearch import Elasticsearch
from openai import OpenAI

from core.models import Country, Event, RawPost, Statement
from core.services.summary_service import (
    regenerate_country_event_summary,
)

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(
    os.getenv(
        "CELERY_BROKER_URL",
        "redis://localhost:6379/0",
    )
)

CLASSIFY_LOCK_KEY = "classify_rawposts_running"

CLASSIFY_LOCK_TTL = 60 * 30  # 30 mins
SUMMARY_LOCK_TTL = 60 * 10  # 10 mins


@shared_task
def sync_diplomaticpulse_to_rawpost():

    countries = {
        "Republic of India": "India",
        "People's Republic of China": "China",
        "United States": "United States of America",
        "Russian Federation": "Russia",
        "Islamic Republic of Iran": "Iran",
        "Syrian Arab Republic": "Syria",
        "Republic of Korea": "South Korea",
        "Democratic People's Republic of Korea": "North Korea",
        "Plurinational State of Bolivia": "Bolivia",
        "Bolivarian Republic of Venezuela": "Venezuela",
        "United Republic of Tanzania": "Tanzania",
        "Republic of Moldova": "Moldova",
        "Socialist Republic of Viet Nam": "Vietnam",
        "Lao People's Democratic Republic": "Laos",
        "Brunei Darussalam": "Brunei",
        "Republic of Cabo Verde": "Cape Verde",
        "Republic of Côte d'Ivoire": "Ivory Coast",
        "Czech Republic": "Czech Republic",
        "United States of America": "United States",
        (
            "United Kingdom of Great Britain "
            "and Northern Ireland"
        ): "United Kingdom",
        "State of Palestine": "Palestine",
        "Federated States of Micronesia": "Micronesia",
        (
            "Republic of Trinidad and Tobago"
        ): "Trinidad",
        "Republic of Türkiye": "Turkey",
        "Federal Republic of Germany": "Germany",
        "French Republic": "France",
        "Federative Republic of Brazil": "Brazil",
        "Islamic Republic of Pakistan": "Pakistan",
        "People's Republic of Bangladesh": "Bangladesh",
        "Kingdom of Saudi Arabia": "Saudi Arabia",
        "Japan": "Japan",
        "Commonwealth of Australia": "Australia",
        "Canada": "Canada",
        "United Mexican States": "Mexico",
        "Argentine Republic": "Argentina",
    }

    es = Elasticsearch(
        hosts=[os.getenv("ELASTIC_HOST")],
        http_auth=(
            os.getenv("ELASTIC_USERNAME"),
            os.getenv("ELASTIC_PASSWORD"),
        ),
        verify_certs=False,
        timeout=30,
    )

    page_size = 100
    page = 0
    created = 0
    skipped = 0

    while True:

        result = es.search(
            index="dppa.st",
            body={"query": {"match_all": {}}},
            size=page_size,
            from_=page * page_size,
        )

        hits = result["hits"]["hits"]

        if not hits:
            break

        for hit in hits:

            src = hit["_source"]

            url = src.get("url", "").strip()

            if not url:
                skipped += 1
                continue

            # Use URL hash as unique post_id
            post_id = hashlib.md5(
                url.encode()
            ).hexdigest()

            # Skip if already synced
            if RawPost.objects.filter(
                post_id=post_id
            ).exists():
                skipped += 1
                continue

            country_name = countries.get(
                src.get("country", "").strip(),
                src.get("country", "").strip(),
            )

            country = Country.objects.filter(
                name__iexact=country_name
            ).first()

            if not country:

                logger.warning(
                    "Country not found: %s",
                    country_name,
                )

                skipped += 1
                continue

            # Parse date
            try:
                posted_at = timezone.make_aware(
                    datetime.strptime(
                        src.get("posted_date", ""),
                        "%Y-%m-%d",
                    ),
                    timezone.get_current_timezone(),
                )

            except (ValueError, TypeError):
                posted_at = timezone.now()

            RawPost.objects.create(
                country=country,
                platform="web",
                account_handle="",
                post_id=post_id,
                post_text=src.get("statement", ""),
                combined_text=src.get("statement", ""),
                posted_at=posted_at,
                post_url=url,
                source_url=url,
                title=src.get("title", ""),
                language=src.get("language", ""),
                content_type=src.get(
                    "content_type",
                    "",
                ),
                classify_ai_processed=False,
            )

            created += 1

        page += 1

    logger.info(
        "Sync complete: %s created, %s skipped",
        created,
        skipped,
    )

    return {
        "created": created,
        "skipped": skipped,
    }


def get_nvidia_client():

    nvidia_api_key = os.getenv(
        "NVIDIA_NIM_API_KEY"
    )

    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=nvidia_api_key,
    )


def build_prompt(post, event_list_text):

    text = (
        post.combined_text
        or post.post_text
        or ""
    ).strip()

    return f"""
You are a senior geopolitical intelligence analyst
specializing in diplomatic communications and
international relations.

TASK:
Analyze the following official diplomatic statement
and extract structured intelligence.

---
STATEMENT DETAILS:
- Country: {post.country.full_name or post.country.name}
- Source URL: {post.post_url}
- Language: {getattr(post, 'language', 'Unknown')}
- Posted: {post.posted_at.strftime('%B %d, %Y')}
- Raw Text (first 2000 chars): {text[:2000]}
---

KNOWN GEOPOLITICAL EVENTS (choose ONE most relevant, or null if none fit):
{event_list_text}

---
ANALYSIS INSTRUCTIONS:
1. Read the statement carefully. If it is not in English, analyze the meaning.
2. Match it to ONE event even if the event is referenced INDIRECTLY — "
"through geography (e.g. 'Strait of Hormuz'), organizations (e.g. 'IRGC'), "
"or related terminology (e.g. 'West Asia tensions', 'Gulf escalation').
3. Determine the country's STANCE toward that event:
   - "support" → endorses, agrees with, or backs the position/event
   - "oppose"  → criticizes, condemns, or stands against it
   - "neutral" → acknowledges without clear side, or is about unrelated bilateral matters
4. Write a concise 2-3 sentence English summary.
5. Extract 3-5 key topics (countries, orgs, conflicts, treaties mentioned).
6. Rate confidence 0.0-1.0 on how clearly this statement relates to the chosen event.

RULES:
- If statement is about routine bilateral trade/cultural ties not related to any event → event_id: null, stance: "neutral"
- Do NOT guess or hallucinate events not in the list
- Confidence < 0.5 = weak or ambiguous link
- ONLY return valid JSON, no extra text, no markdown

Respond in this exact JSON format:
{{
  "event_id": <integer or null>,
  "event_title": "<matched event title or none>",
  "stance": "support" | "neutral" | "oppose",
  "confidence": <float 0.0-1.0>,
  "summary": "<2-3 sentence English summary>",
  "topics": ["<topic1>", "<topic2>", "<topic3>"],
  "reasoning": "<1 sentence: why this event and stance>"
}}"""


@shared_task
def classify_rawposts_with_ai(batch_size=25):

    redis_client.setex(
        CLASSIFY_LOCK_KEY,
        CLASSIFY_LOCK_TTL,
        "1",
    )

    try:

        client = get_nvidia_client()

        unprocessed = list(
            RawPost.objects.filter(
                classify_ai_processed=False
            )
            .select_related("country")[:batch_size]
        )

        if not unprocessed:

            logger.info(
                "No unprocessed RawPosts found."
            )

            return {"processed": 0}

        events = list(
            Event.objects.values(
                "id",
                "title",
                "description",
                "start_date",
            )
        )

        if not events:

            logger.warning(
                "No Events found in DB."
            )

            return {
                "error": "No events in DB"
            }

        event_list_text = "\n".join(
            [
                (
                    f"[ID:{e['id']}] "
                    f"{e['title']} — "
                    f"{e['description']} "
                    f"(since {e['start_date']})"
                )
                for e in events
            ]
        )

        posts_text = ""

        for i, post in enumerate(unprocessed):

            text = (
                post.combined_text
                or post.post_text
                or ""
            ).strip()[:1000]

            posts_text += f"""
POST_INDEX: {i}
Country: {post.country.name}
Text: {text}
---
"""

        prompt = f"""
You are a geopolitical intelligence analyst.

KNOWN GEOPOLITICAL EVENTS:
{event_list_text}

Analyze EACH diplomatic post.

POSTS:
{posts_text}

Return a JSON ARRAY:
[
  {{
    "post_index": 0,
    "event_id": <integer or null>,
    "stance": "support" | "neutral" | "oppose",
    "confidence": <float 0.0-1.0>,
    "summary": "<2-3 sentence English summary>",
    "topics": ["topic1", "topic2"],
    "reasoning": "<1 sentence>"
  }},
  ...
]

RULES:
- Return exactly {len(unprocessed)} objects in the array
- Same order as posts (post_index must match)
- If no event matches → event_id: null, stance: "neutral", confidence: 0.0
- ONLY valid JSON array, no markdown, no extra text
"""

        response = (
            client.chat.completions.create(
                model=(
                    "meta/llama-3.3-70b-instruct"
                ),
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return only valid JSON."
                        ),
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                temperature=0.1,
                max_tokens=8192,
            )
        )

        raw = (
            response.choices[0]
            .message.content.strip()
        )

        if "```" in raw:

            raw = raw.split("```")[1]

            if raw.startswith("json"):
                raw = raw[4:]

            raw = raw.strip()

        results = json.loads(raw)

        processed = 0
        created_statements = 0
        failed = 0

        for item in results:

            idx = item.get("post_index")

            if (
                idx is None
                or idx >= len(unprocessed)
            ):
                continue

            post = unprocessed[idx]

            try:

                stance = item.get(
                    "stance",
                    "neutral",
                )

                if stance not in (
                    "support",
                    "neutral",
                    "oppose",
                ):
                    stance = "neutral"

                confidence = float(
                    item.get("confidence", 0.0)
                )

                event_id = item.get("event_id")

                event = None

                if event_id:
                    event = Event.objects.filter(
                        id=event_id
                    ).first()

                if event and confidence >= 0.5:

                    Statement.objects.get_or_create(
                        source_url=post.post_url,
                        defaults={
                            "raw_post": post,
                            "country": post.country,
                            "event": event,
                            "text": (
                                post.combined_text
                                or post.post_text
                                or ""
                            ),
                            "stance": stance,
                            "confidence_score": (
                                confidence
                            ),
                            "summary": item.get(
                                "summary",
                                "",
                            ),
                            "topics": item.get(
                                "topics",
                                [],
                            ),
                            "publish_date": (
                                post.posted_at.date()
                            ),
                        },
                    )

                    created_statements += 1

                    logger.info(
                        "[%s] stance=%s conf=%.2f",
                        post.country.name,
                        stance,
                        confidence,
                    )

                else:

                    logger.info(
                        (
                            "[%s] No match or "
                            "low confidence %.2f"
                        ),
                        post.country.name,
                        confidence,
                    )

                processed += 1

                post.classify_ai_processed = True
                post.save()

            except Exception as exc:

                logger.error(
                    (
                        "Error processing "
                        "post index %s: %s"
                    ),
                    idx,
                    exc,
                )

                failed += 1

        logger.info(
            (
                "Batch done — "
                "Processed: %s | "
                "Created: %s | "
                "Failed: %s"
            ),
            processed,
            created_statements,
            failed,
        )

        return {
            "processed": processed,
            "statements_created": (
                created_statements
            ),
            "failed": failed,
        }

    except json.JSONDecodeError as exc:

        logger.error(
            "JSON parse failed: %s",
            exc,
        )

        return {
            "error": "json_parse_failed"
        }

    except Exception as exc:

        logger.error(
            "classify task error: %s",
            exc,
        )

        return {"error": str(exc)}

    finally:

        redis_client.delete(
            CLASSIFY_LOCK_KEY
        )

        logger.info(
            "Classify lock released."
        )


@shared_task
def sync_and_classify():

    if redis_client.exists(
        CLASSIFY_LOCK_KEY
    ):

        logger.info(
            (
                "Classify still running. "
                "Skipping sync."
            )
        )

        return {
            "skipped": True,
            "reason": "classify_locked",
        }

    sync_result = (
        sync_diplomaticpulse_to_rawpost()
    )

    logger.info(
        "Sync done: %s",
        sync_result,
    )

    classify_rawposts_with_ai.delay()

    return {
        "sync": sync_result,
        "classify": "queued",
    }


@shared_task
def regenerate_summary_task(
    country_id,
    event_id,
):

    lock_key = (
        f"summary_lock:{country_id}:{event_id}"
    )

    if redis_client.exists(lock_key):

        logger.info(
            (
                "Summary regeneration skipped "
                "(debounced): %s"
            ),
            lock_key,
        )

        return {
            "skipped": True,
            "reason": "debounced",
        }

    redis_client.setex(
        lock_key,
        SUMMARY_LOCK_TTL,
        "1",
    )

    try:

        country = Country.objects.get(
            id=country_id
        )

        event = Event.objects.get(
            id=event_id
        )

        regenerate_country_event_summary(
            country,
            event,
        )

        logger.info(
            "Summary regenerated: %s | %s",
            country.name,
            event.title,
        )

        return {"success": True}

    except Exception as exc:

        logger.error(
            "Summary regeneration failed: %s",
            str(exc),
        )

        return {
            "success": False,
            "error": str(exc),
        }
