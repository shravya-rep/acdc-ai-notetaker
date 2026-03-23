"""
Meeting type classifier — fast keyword pass, LLM fallback for ambiguous cases.
"""
import logging
from apps.meetings.models import Meeting

logger = logging.getLogger(__name__)

# Keyword rules: meeting_type -> list of title keywords (lowercase)
KEYWORD_RULES = {
    Meeting.MeetingType.STANDUP: ["standup", "stand-up", "stand up", "daily scrum", "daily sync"],
    Meeting.MeetingType.PLANNING: ["planning", "sprint planning", "roadmap", "kickoff", "kick-off", "backlog"],
    Meeting.MeetingType.MENTORING: ["mentoring", "mentor", "1:1", "one on one", "one-on-one", "coaching", "career"],
    Meeting.MeetingType.OPERATIONS: ["operations", "ops", "incident", "postmortem", "post-mortem", "retro", "retrospective"],
    Meeting.MeetingType.SYNC: ["sync", "check-in", "check in", "weekly", "update", "status"],
}


def classify_by_keywords(title: str) -> str | None:
    """Return a MeetingType if title matches a keyword rule, else None."""
    title_lower = title.lower()
    for meeting_type, keywords in KEYWORD_RULES.items():
        if any(kw in title_lower for kw in keywords):
            return meeting_type
    return None


def classify_by_llm(title: str, transcript_snippet: str, duration_minutes: int) -> str:
    """Use LLM to classify ambiguous meetings. Returns a MeetingType value."""
    from django.conf import settings

    prompt = f"""Classify this meeting into exactly one of these types:
standup, planning, sync, mentoring, operations, general

Meeting title: {title}
Duration: {duration_minutes} minutes
Transcript snippet (first 500 chars): {transcript_snippet[:500]}

Reply with only the single word type."""

    try:
        if settings.LLM_PROVIDER == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            response = client.messages.create(
                model=settings.LLM_MODEL,
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}],
            )
            result = response.content[0].text.strip().lower()
        else:
            import openai
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=settings.LLM_MODEL,
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}],
            )
            result = response.choices[0].message.content.strip().lower()

        valid_types = [t.value for t in Meeting.MeetingType]
        if result in valid_types:
            return result
    except Exception as e:
        logger.warning(f"LLM classification failed: {e}")

    return Meeting.MeetingType.GENERAL


def classify_meeting_type(title: str, transcript: str = "", duration_minutes: int = 0) -> str:
    """
    Classify a meeting into a MeetingType.
    Fast keyword pass first; falls back to LLM for ambiguous cases.
    """
    keyword_result = classify_by_keywords(title)
    if keyword_result:
        logger.info(f"Classified '{title}' as '{keyword_result}' via keywords")
        return keyword_result

    llm_result = classify_by_llm(title, transcript, duration_minutes)
    logger.info(f"Classified '{title}' as '{llm_result}' via LLM")
    return llm_result
