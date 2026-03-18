import msal
from django.conf import settings


def get_app_token():
    """Get application-level token for Graph API (daemon/service)."""
    app = msal.ConfidentialClientApplication(
        settings.AZURE_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}",
        client_credential=settings.AZURE_CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    if "access_token" not in result:
        raise RuntimeError(f"Failed to acquire Graph token: {result.get('error_description')}")
    return result["access_token"]


def get_graph_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
