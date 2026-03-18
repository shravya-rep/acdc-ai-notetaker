from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Meeting, ActionItem
from .serializers import MeetingListSerializer, MeetingDetailSerializer, ActionItemSerializer


class MeetingListView(generics.ListAPIView):
    serializer_class = MeetingListSerializer
    queryset = Meeting.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        meeting_type = self.request.query_params.get("type")
        state = self.request.query_params.get("state")
        if meeting_type:
            qs = qs.filter(meeting_type=meeting_type)
        if state:
            qs = qs.filter(state=state)
        return qs


class MeetingDetailView(generics.RetrieveAPIView):
    serializer_class = MeetingDetailSerializer
    queryset = Meeting.objects.prefetch_related("attendees", "recap__tracked_actions")
    lookup_field = "pk"


class ActionItemListView(generics.ListAPIView):
    serializer_class = ActionItemSerializer

    def get_queryset(self):
        return ActionItem.objects.filter(
            recap__meeting__attendees__email=self.request.user.email,
            completed=False,
        ).select_related("recap__meeting")


@api_view(["PATCH"])
def complete_action_item(request, pk):
    try:
        item = ActionItem.objects.get(pk=pk)
    except ActionItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    item.completed = True
    item.save(update_fields=["completed", "updated_at"])
    return Response(ActionItemSerializer(item).data)
