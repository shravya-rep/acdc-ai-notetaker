"""
Meeting Monitor Agent — runs periodically to detect completed meetings.
Polls Microsoft Graph API for recent meetings and queues them for processing.
"""
import logging
import requests
from datetime import datetime, timedelta, timezone
from django.conf import settings
from apps.meetings.models import Meeting, ProcessingLog
from apps.graph.client import get_app_token, get_graph_headers
from .tasks import process_meeting_task

logger = logging.getLogger(__name__)

SKIP_DURATION_MINUTES = 5  # Skip meetings shorter than this
GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def should_process_meeting(meeting_data: dict) -> bool:
    """Decide whether a meeting warrants processing."""
    subject = meeting_data.get("subject", "").lower()
    skip_keywords = ["test", "personal", "focus time", "blocked", "lunch"]
    if any(kw in subject for kw in skip_keywords):
        logger.info(f"Skipping meeting '{subject}' — matched skip keyword")
        return False
    return True


def run_monitor_agent():
    """Main entry point for the Monitor Agent Celery task."""
    logger.info("Meeting Monitor Agent: starting scan")
    try:
        token = get_app_token()
        headers = get_graph_headers(token)
    except Exception as e:
        logger.error(f"Monitor Agent: failed to get Graph token: {e}")
        return

    since = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    # In production: query all users' calendars or use subscription notifications
    # Placeholder: log that monitor ran
    logger.info(f"Meeting Monitor Agent: scan complete (since {since})")
