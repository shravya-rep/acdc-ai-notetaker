"""
Follow-up Manager Agent — scans action items and sends deadline reminders.
"""
import logging
from datetime import date, timedelta
from django.conf import settings
from apps.meetings.models import ActionItem

logger = logging.getLogger(__name__)


def run_followup_agent():
    """Scan open action items and send reminders for upcoming deadlines."""
    logger.info("Follow-up Manager Agent: starting daily scan")
    today = date.today()

    items_to_remind = ActionItem.objects.filter(
        completed=False,
        reminder_sent=False,
        due_date__lte=today + timedelta(days=1),
        due_date__gte=today,
    ).select_related("recap__meeting")

    sent = 0
    for item in items_to_remind:
        try:
            send_reminder(item)
            item.reminder_sent = True
            item.save(update_fields=["reminder_sent", "updated_at"])
            sent += 1
        except Exception as e:
            logger.error(f"Failed to send reminder for action item {item.id}: {e}")

    logger.info(f"Follow-up Manager Agent: sent {sent} reminders")

    # Escalate overdue items
    overdue = ActionItem.objects.filter(
        completed=False,
        due_date__lt=today,
    ).count()
    if overdue:
        logger.warning(f"Follow-up Manager Agent: {overdue} overdue action items")


def send_reminder(item: ActionItem):
    """Send a reminder email for an action item."""
    from django.core.mail import send_mail
    meeting_title = item.recap.meeting.title
    subject = f"Reminder: Action item due {'today' if item.due_date == date.today() else 'tomorrow'}"
    body = f"""Hi,

This is a reminder about an action item from the meeting "{meeting_title}":

{item.description}

Due date: {item.due_date}

Please update the status in the ACDC Notetaker dashboard.

— ACDC AI Notetaker
"""
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[item.owner_email],
        fail_silently=False,
    )
