import os

import msal
import requests
from authlib.integrations.requests_client import OAuth2Session

MICROSOFT_AUTHORITY = os.getenv(
    "MICROSOFT_AUTHORITY", "https://login.microsoftonline.com/common"
)
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET")
MICROSOFT_SCOPES = (
    os.getenv("MICROSOFT_SCOPES") or "openid email profile offline_access User.Read"
).split()
MICROSOFT_REDIRECT_URI = os.getenv("MICROSOFT_REDIRECT_URI")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_SCOPES = ["openid", "email", "profile"]


def ms_build_auth_url(state: str) -> str:
    app = msal.ConfidentialClientApplication(
        MICROSOFT_CLIENT_ID,
        authority=MICROSOFT_AUTHORITY,
        client_credential=MICROSOFT_CLIENT_SECRET,
    )
    return app.get_authorization_request_url(
        scopes=MICROSOFT_SCOPES,
        redirect_uri=MICROSOFT_REDIRECT_URI,
        state=state,
        response_mode="query",
        prompt=None,
    )


def ms_exchange_code_for_token(code: str) -> dict:
    app = msal.ConfidentialClientApplication(
        MICROSOFT_CLIENT_ID,
        authority=MICROSOFT_AUTHORITY,
        client_credential=MICROSOFT_CLIENT_SECRET,
    )
    return app.acquire_token_by_authorization_code(
        code=code,
        scopes=MICROSOFT_SCOPES,
        redirect_uri=MICROSOFT_REDIRECT_URI,
    )


def ms_userinfo(access_token: str) -> dict:
    r = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )
    r.raise_for_status()
    me = r.json()
    return {
        "name": me.get("displayName"),
        "email": me.get("mail") or me.get("userPrincipalName"),
        "id": me.get("id"),
        "raw": me,
    }


def google_build_auth_url(state: str) -> tuple[str, str]:
    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        scope=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI,
    )
    uri, st_val = oauth.create_authorization_url(
        GOOGLE_AUTH_URL,
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
        state=state,
    )
    return uri, st_val


def google_exchange_code_for_token(code: str) -> dict:
    oauth = OAuth2Session(
        GOOGLE_CLIENT_ID,
        GOOGLE_CLIENT_SECRET,
        scope=GOOGLE_SCOPES,
        redirect_uri=GOOGLE_REDIRECT_URI,
    )
    return oauth.fetch_token(GOOGLE_TOKEN_URL, code=code)


def google_userinfo(access_token: str) -> dict:
    """
    Fetch Google userinfo using the OpenID Connect userinfo endpoint.
    """
    r = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=20,
    )
    r.raise_for_status()
    me = r.json()
    return {
        "name": me.get("name") or me.get("given_name"),
        "email": me.get("email"),
        "id": me.get("sub"),
        "raw": me,
    }
