import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_meeting_task(self, meeting_id: int):
    """Process a meeting: fetch transcript, generate recap, send email."""
    from apps.meetings.models import Meeting, ProcessingLog
    from apps.agents.recap_generator import generate_recap, store_recap

    try:
        meeting = Meeting.objects.get(pk=meeting_id)
        meeting.state = Meeting.State.PROCESSING
        meeting.save(update_fields=["state"])

        ProcessingLog.objects.create(
            meeting=meeting,
            event_type=ProcessingLog.EventType.QUEUED,
            status="started",
        )

        recap_data = generate_recap(meeting)
        recap = store_recap(meeting, recap_data)

        meeting.state = Meeting.State.COMPLETED
        meeting.save(update_fields=["state"])

        send_recap_email.delay(recap.id)

        ProcessingLog.objects.create(
            meeting=meeting,
            event_type=ProcessingLog.EventType.COMPLETED,
            status="success",
        )

    except Exception as exc:
        logger.error(f"process_meeting_task failed for meeting {meeting_id}: {exc}")
        try:
            meeting = Meeting.objects.get(pk=meeting_id)
            meeting.state = Meeting.State.FAILED
            meeting.save(update_fields=["state"])
        except Exception:
            pass
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_recap_email(self, recap_id: int):
    """Send recap email to all meeting attendees."""
    from apps.meetings.models import Recap
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        recap = Recap.objects.select_related("meeting").prefetch_related("meeting__attendees").get(pk=recap_id)
        meeting = recap.meeting
        recipients = list(meeting.attendees.values_list("email", flat=True))

        subject = f"Meeting Recap: {meeting.title}"
        body = f"""Meeting Recap: {meeting.title}
Date: {meeting.start_time.strftime('%B %d, %Y %H:%M UTC')}

SUMMARY
{recap.summary}

KEY DECISIONS
{chr(10).join(f'• {d}' for d in recap.decisions) or 'None recorded'}

ACTION ITEMS
{chr(10).join(f'• {a["description"]} — {a.get("owner", "TBD")} (due: {a.get("due_date", "TBD")})' for a in recap.action_items) or 'None recorded'}

OPEN QUESTIONS
{chr(10).join(f'• {q}' for q in recap.open_questions) or 'None recorded'}

— ACDC AI Notetaker
"""
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def run_monitor_agent_task():
    """Periodic task: Meeting Monitor Agent."""
    from apps.agents.monitor import run_monitor_agent
    run_monitor_agent()


@shared_task
def run_followup_agent_task():
    """Periodic task: Follow-up Manager Agent (runs daily)."""
    from apps.agents.followup_manager import run_followup_agent
    run_followup_agent()


@shared_task(bind=True, max_retries=5, default_retry_delay=300)
def process_meeting_webhook(self, notification: dict):
    """Handle incoming Graph webhook notification."""
    logger.info(f"Received Graph webhook: {notification.get('changeType')} on {notification.get('resource')}")
