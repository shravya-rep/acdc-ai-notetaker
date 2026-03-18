from rest_framework import serializers
from .models import Meeting, Attendee, Recap, ActionItem


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = ["id", "name", "email", "attended"]


class ActionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionItem
        fields = ["id", "description", "owner_email", "owner_name", "due_date", "completed", "reminder_sent"]


class RecapSerializer(serializers.ModelSerializer):
    tracked_actions = ActionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Recap
        fields = ["id", "summary", "decisions", "action_items", "open_questions", "key_topics", "tracked_actions", "created_at"]


class MeetingListSerializer(serializers.ModelSerializer):
    has_recap = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = ["id", "title", "start_time", "duration_minutes", "meeting_type", "state", "has_recap"]

    def get_has_recap(self, obj):
        return hasattr(obj, "recap")


class MeetingDetailSerializer(serializers.ModelSerializer):
    attendees = AttendeeSerializer(many=True, read_only=True)
    recap = RecapSerializer(read_only=True)

    class Meta:
        model = Meeting
        fields = ["id", "graph_meeting_id", "title", "start_time", "end_time", "duration_minutes",
                  "meeting_type", "state", "attendees", "recap", "created_at"]
