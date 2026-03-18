from django.db import models
from apps.users.models import User


class Meeting(models.Model):
    class State(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"
        FAILED = "failed", "Failed"

    class MeetingType(models.TextChoices):
        STANDUP = "standup", "Standup"
        PLANNING = "planning", "Planning"
        SYNC = "sync", "Sync"
        MENTORING = "mentoring", "Mentoring"
        OPERATIONS = "operations", "Operations"
        GENERAL = "general", "General"

    graph_meeting_id = models.CharField(max_length=512, unique=True)
    title = models.CharField(max_length=500)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="organized_meetings")
    state = models.CharField(max_length=20, choices=State.choices, default=State.PENDING)
    meeting_type = models.CharField(max_length=20, choices=MeetingType.choices, default=MeetingType.GENERAL)
    transcript_available = models.BooleanField(default=False)
    raw_transcript = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "meetings"
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.title} ({self.start_time.date()})"


class Attendee(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="attendees")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    attended = models.BooleanField(default=True)

    class Meta:
        db_table = "attendees"
        unique_together = ["meeting", "email"]


class Recap(models.Model):
    meeting = models.OneToOneField(Meeting, on_delete=models.CASCADE, related_name="recap")
    summary = models.TextField()
    decisions = models.JSONField(default=list)
    action_items = models.JSONField(default=list)
    open_questions = models.JSONField(default=list)
    key_topics = models.JSONField(default=list)
    llm_model_used = models.CharField(max_length=100, blank=True)
    generation_time_ms = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "recaps"


class ActionItem(models.Model):
    recap = models.ForeignKey(Recap, on_delete=models.CASCADE, related_name="tracked_actions")
    description = models.TextField()
    owner_email = models.EmailField()
    owner_name = models.CharField(max_length=255, blank=True)
    due_date = models.DateField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "action_items"
        ordering = ["due_date"]


class ProcessingLog(models.Model):
    class EventType(models.TextChoices):
        DETECTED = "detected", "Meeting Detected"
        QUEUED = "queued", "Queued for Processing"
        TRANSCRIPT_FETCH = "transcript_fetch", "Transcript Fetch"
        LLM_CALL = "llm_call", "LLM Call"
        EMAIL_SENT = "email_sent", "Email Sent"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        SKIPPED = "skipped", "Skipped"

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="logs")
    event_type = models.CharField(max_length=30, choices=EventType.choices)
    status = models.CharField(max_length=20)
    message = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "processing_logs"
        ordering = ["-created_at"]
