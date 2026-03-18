import msal
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserPreference
from .serializers import UserSerializer, UserPreferenceSerializer


def get_msal_app():
    return msal.ConfidentialClientApplication(
        settings.AZURE_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}",
        client_credential=settings.AZURE_CLIENT_SECRET,
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_login(request):
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        scopes=["User.Read", "Calendars.Read", "OnlineMeetings.Read"],
        redirect_uri=settings.AZURE_REDIRECT_URI,
    )
    return Response({"auth_url": auth_url})


@api_view(["GET"])
@permission_classes([AllowAny])
def auth_callback(request):
    code = request.GET.get("code")
    if not code:
        return Response({"error": "No code provided"}, status=status.HTTP_400_BAD_REQUEST)

    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=["User.Read", "Calendars.Read", "OnlineMeetings.Read"],
        redirect_uri=settings.AZURE_REDIRECT_URI,
    )

    if "error" in result:
        return Response({"error": result.get("error_description")}, status=status.HTTP_400_BAD_REQUEST)

    ms_user = result.get("id_token_claims", {})
    user, _ = User.objects.get_or_create(
        microsoft_id=ms_user.get("oid"),
        defaults={
            "email": ms_user.get("preferred_username", ""),
            "first_name": ms_user.get("given_name", ""),
            "last_name": ms_user.get("family_name", ""),
            "username": ms_user.get("preferred_username", ""),
        },
    )
    UserPreference.objects.get_or_create(user=user)

    refresh = RefreshToken.for_user(user)
    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": UserSerializer(user).data,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_preferences(request):
    prefs, _ = UserPreference.objects.get_or_create(user=request.user)
    serializer = UserPreferenceSerializer(prefs, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
