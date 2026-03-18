"""
Recap Generator Agent — fetches transcript, calls LLM, stores structured recap.
"""
import logging
import json
import time
from django.conf import settings
from apps.meetings.models import Meeting, Recap, ActionItem, ProcessingLog

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert meeting analyst. Extract a structured recap from the meeting transcript.

Return valid JSON with this exact structure:
{
  "summary": "2-3 paragraph overview of the meeting",
  "decisions": ["decision 1", "decision 2"],
  "action_items": [
    {"description": "task", "owner": "name or email", "due_date": "YYYY-MM-DD or null"}
  ],
  "open_questions": ["question 1", "question 2"],
  "key_topics": ["topic 1", "topic 2"],
  "meeting_type": "standup|planning|sync|mentoring|operations|general"
}"""


def get_llm_client():
    if settings.LLM_PROVIDER == "anthropic":
        import anthropic
        return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    else:
        import openai
        return openai.OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_recap(meeting: Meeting) -> dict:
    """Call LLM to generate structured recap from transcript."""
    if not meeting.raw_transcript:
        raise ValueError(f"No transcript available for meeting {meeting.id}")

    prompt = f"""Meeting: {meeting.title}
Date: {meeting.start_time.strftime('%Y-%m-%d %H:%M UTC')}
Duration: {meeting.duration_minutes} minutes

TRANSCRIPT:
{meeting.raw_transcript}

Generate a structured recap as JSON."""

    start = time.time()
    client = get_llm_client()

    if settings.LLM_PROVIDER == "anthropic":
        response = client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
            system=SYSTEM_PROMPT,
        )
        content = response.content[0].text
    else:
        response = client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content

    elapsed_ms = int((time.time() - start) * 1000)
    data = json.loads(content)
    data["generation_time_ms"] = elapsed_ms
    data["llm_model"] = settings.LLM_MODEL
    return data


def store_recap(meeting: Meeting, data: dict) -> Recap:
    """Persist the generated recap and action items."""
    recap, _ = Recap.objects.update_or_create(
        meeting=meeting,
        defaults={
            "summary": data.get("summary", ""),
            "decisions": data.get("decisions", []),
            "action_items": data.get("action_items", []),
            "open_questions": data.get("open_questions", []),
            "key_topics": data.get("key_topics", []),
            "llm_model_used": data.get("llm_model", ""),
            "generation_time_ms": data.get("generation_time_ms"),
        },
    )

    for item in data.get("action_items", []):
        ActionItem.objects.get_or_create(
            recap=recap,
            description=item.get("description", ""),
            owner_email=item.get("owner", ""),
            defaults={
                "owner_name": item.get("owner", ""),
                "due_date": item.get("due_date"),
            },
        )

    return recap
