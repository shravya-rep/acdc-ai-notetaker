from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import hmac
import hashlib
from apps.agents.tasks import process_meeting_webhook


@api_view(["POST", "GET"])
def webhook_endpoint(request):
    """Handle Microsoft Graph change notifications."""
    # Validation token handshake (required by Graph)
    validation_token = request.query_params.get("validationToken")
    if validation_token:
        return Response(validation_token, content_type="text/plain", status=status.HTTP_200_OK)

    notifications = request.data.get("value", [])
    for notification in notifications:
        resource = notification.get("resource", "")
        if "onlineMeetings" in resource or "callRecords" in resource:
            process_meeting_webhook.delay(notification)

    return Response(status=status.HTTP_202_ACCEPTED)
