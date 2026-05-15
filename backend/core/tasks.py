# core/tasks.py
import hashlib
import os
from celery import shared_task
from elasticsearch import Elasticsearch
from django.conf import settings
from .models import RawPost, Country
from datetime import datetime
import logging
import time
import json
from core.models import Event, Statement
from openai import OpenAI
from django.utils import timezone
from datetime import datetime
import redis
from core.services.summary_service import (
    regenerate_country_event_summary
)

logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url(os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"))

CLASSIFY_LOCK_KEY = "classify_rawposts_running"
CLASSIFY_LOCK_TTL = 60 * 30  # 30 min max lock (safety valve)
SUMMARY_LOCK_TTL = 60 * 10  # 10 mins


@shared_task
def sync_diplomaticpulse_to_rawpost():
    COUNTRIES = {
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
        "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
        "State of Palestine": "Palestine",
        "Federated States of Micronesia": "Micronesia",
        "Republic of Trinidad and Tobago": "Trinidad",
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
        http_auth=(os.getenv("ELASTIC_USERNAME"), os.getenv("ELASTIC_PASSWORD")),
        verify_certs=False,
        timeout=30
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
            from_=page * page_size
        )

        hits = result['hits']['hits']
        if not hits:
            break

        for hit in hits:
            src = hit['_source']
            url = src.get('url', '').strip()
            if not url:
                skipped += 1
                continue

            # Use URL hash as unique post_id
            post_id = hashlib.md5(url.encode()).hexdigest()

            # Skip if already synced
            if RawPost.objects.filter(post_id=post_id).exists():
                skipped += 1
                continue

            country_name = COUNTRIES.get(src.get('country', '').strip(), src.get('country', '').strip())
            # Match country
            country = Country.objects.filter(
                name__iexact=country_name
            ).first()

            if not country:
                logger.warning(f"Country not found: {country_name}")
                skipped += 1
                continue

            # Parse date
            try:
                posted_at = timezone.make_aware(
                    datetime.strptime(src.get('posted_date', ''), '%Y-%m-%d'),
                    timezone.get_current_timezone()
                )
            except (ValueError, TypeError):
                posted_at = datetime.now()

            RawPost.objects.create(
                country=country,
                platform='web',
                account_handle='',
                post_id=post_id,
                post_text=src.get('statement', ''),
                combined_text=src.get('statement', ''),
                posted_at=posted_at,
                post_url=url,
                source_url=url,
                title=src.get('title', ''),
                language=src.get('language', ''),
                content_type=src.get('content_type', ''),
                classify_ai_processed=False,   # AI hasn't processed yet
            )
            created += 1

        page += 1

    logger.info(f"Sync complete: {created} created, {skipped} skipped")
    return {"created": created, "skipped": skipped}


def get_nvidia_client():
    NVIDIA_NIM_API_KEY = os.getenv("NVIDIA_NIM_API_KEY")
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=NVIDIA_NIM_API_KEY
    )

def build_prompt(post, event_list_text):
    text = (post.combined_text or post.post_text or '').strip()
    return f"""You are a senior geopolitical intelligence analyst specializing in diplomatic communications and international relations.

TASK:
Analyze the following official diplomatic statement and extract structured intelligence.

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
    redis_client.setex(CLASSIFY_LOCK_KEY, CLASSIFY_LOCK_TTL, "1")

    try:
        client = get_nvidia_client()

        unprocessed = list(
            RawPost.objects.filter(classify_ai_processed=False)
            .select_related('country')[:batch_size]
        )

        if not unprocessed:
            logger.info("No unprocessed RawPosts found.")
            return {"processed": 0}

        events = list(Event.objects.values('id', 'title', 'description', 'start_date'))
        if not events:
            logger.warning("No Events found in DB.")
            return {"error": "No events in DB"}

        event_list_text = "\n".join([
            f"[ID:{e['id']}] {e['title']} — {e['description']} (since {e['start_date']})"
            for e in events
        ])

        # Build ONE prompt with all posts
        posts_text = ""
        for i, post in enumerate(unprocessed):
            text = (post.combined_text or post.post_text or '').strip()[:1000]
            posts_text += f"""
POST_INDEX: {i}
Country: {post.country.name}
Text: {text}
---"""

        prompt = f"""You are a geopolitical intelligence analyst.

KNOWN GEOPOLITICAL EVENTS:
{event_list_text}

Analyze EACH of the following diplomatic posts. For each, return a JSON object.

POSTS:
{posts_text}

Return a JSON ARRAY (one object per post, in the same order):
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

        response = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are a geopolitical analyst. Return only a valid JSON array. No markdown."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=8192,  # higher — we need output for all posts
        )

        raw = response.choices[0].message.content.strip()

        # Clean markdown if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        results = json.loads(raw)  # list of dicts

        processed = 0
        created_statements = 0
        failed = 0

        for item in results:
            idx = item.get("post_index")
            if idx is None or idx >= len(unprocessed):
                continue

            post = unprocessed[idx]

            try:
                stance = item.get("stance", "neutral")
                if stance not in ("support", "neutral", "oppose"):
                    stance = "neutral"

                confidence = float(item.get("confidence", 0.0))
                event_id = item.get("event_id")
                event = Event.objects.filter(id=event_id).first() if event_id else None

                if event and confidence >= 0.5:
                    Statement.objects.get_or_create(
                        source_url=post.post_url,
                        defaults={
                            'raw_post': post,
                            'country': post.country,
                            'event': event,
                            'text': (post.combined_text or post.post_text or ''),
                            'stance': stance,
                            'confidence_score': confidence,
                            'summary': item.get('summary', ''),
                            'topics': item.get('topics', []),
                            'publish_date': post.posted_at.date(),
                        }
                    )
                    created_statements += 1
                    logger.info(f"[{post.country.name}] → stance: {stance} | conf: {confidence:.2f}")
                else:
                    logger.info(f"[{post.country.name}] → No match or low confidence ({confidence:.2f})")

                processed += 1
                post.classify_ai_processed = True
                post.save()

            except Exception as e:
                logger.error(f"Error processing post index {idx}: {e}")
                failed += 1

            finally:
                pass
                # post.classify_ai_processed = True
                # post.save()

        logger.info(f"Batch done — Processed: {processed} | Created: {created_statements} | Failed: {failed}")
        return {"processed": processed, "statements_created": created_statements, "failed": failed}

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse failed: {e} | raw: {raw[:300]}")
        return {"error": "json_parse_failed"}

    except Exception as e:
        logger.error(f"classify task error: {e}")
        return {"error": str(e)}

    finally:
        # Always release lock when done
        redis_client.delete(CLASSIFY_LOCK_KEY)
        logger.info("Classify lock released.")


@shared_task
def sync_and_classify():
    # Check if last classify is still running
    if redis_client.exists(CLASSIFY_LOCK_KEY):
        logger.info("Classify still running from last cycle. Skipping this sync.")
        return {"skipped": True, "reason": "classify_locked"}

    # Run sync first
    sync_result = sync_diplomaticpulse_to_rawpost()
    logger.info(f"Sync done: {sync_result}")

    # Kick off classify (it will set/release the lock itself)
    classify_rawposts_with_ai.delay()
    return {"sync": sync_result, "classify": "queued"}


@shared_task
def regenerate_summary_task(country_id, event_id):

    lock_key = f"summary_lock:{country_id}:{event_id}"

    # Skip if recently regenerated
    if redis_client.exists(lock_key):

        logger.info(
            f"Summary regeneration skipped "
            f"(debounced): {lock_key}"
        )

        return {
            "skipped": True,
            "reason": "debounced"
        }

    # Set temporary lock
    redis_client.setex(
        lock_key,
        SUMMARY_LOCK_TTL,
        "1"
    )

    try:

        country = Country.objects.get(id=country_id)

        event = Event.objects.get(id=event_id)

        regenerate_country_event_summary(
            country,
            event
        )

        logger.info(
            f"Summary regenerated: "
            f"{country.name} | {event.title}"
        )

        return {
            "success": True
        }

    except Exception as e:

        logger.error(
            f"Summary regeneration failed: {str(e)}"
        )

        return {
            "success": False,
            "error": str(e)
        }
