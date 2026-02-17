import time

import requests

from app.http_client import Client
from app.tokens import OAuth2Token, token_from_iso


def test_client_uses_requests_session():
    c = Client()
    assert isinstance(c.session, requests.Session)


def test_token_from_iso_uses_dateutil():
    t = token_from_iso("ok", "2099-01-01T00:00:00Z")
    assert isinstance(t, OAuth2Token)
    assert t.access_token == "ok"
    assert not t.expired


def test_api_request_sets_auth_header_when_token_is_valid():
    c = Client()
    c.oauth2_token = OAuth2Token(access_token="ok", expires_at=int(time.time()) + 3600)

    resp = c.request("GET", "/me", api=True)

    assert resp["headers"].get("Authorization") == "Bearer ok"


def test_api_request_refreshes_when_token_is_missing():
    c = Client()
    c.oauth2_token = None

    resp = c.request("GET", "/me", api=True)

    assert resp["headers"].get("Authorization") == "Bearer fresh-token"


def test_api_request_refreshes_when_token_is_dict():
    c = Client()
    c.oauth2_token = {"access_token": "stale", "expires_at": 0}

    resp = c.request("GET", "/me", api=True)

    assert resp["headers"].get("Authorization") == "Bearer fresh-token"



def test_api_request_refreshes_when_token_is_expired():
    c = Client()
    c.oauth2_token = OAuth2Token(access_token="expired", expires_at=int(time.time()) - 3600)

    resp = c.request("GET", "/me", api=True)

    assert resp["headers"].get("Authorization") == "Bearer fresh-token"

def test_api_request_does_not_use_raw_dict_token():
  
    c = Client()
    c.oauth2_token = {
        "access_token": "should-not-be-used",
        "expires_at": int(time.time()) + 3600,
    }

    resp = c.request("GET", "/me", api=True)

    assert resp["headers"].get("Authorization") == "Bearer fresh-token"

def test_api_request_does_not_refresh_when_token_is_valid():
    """
    When oauth2_token is a valid, non-expired OAuth2Token, the client
    should use it as-is (no refresh).
    """
    c = Client()
    token = OAuth2Token(
        access_token="ok",
        expires_at=int(time.time()) + 3600,
    )
    c.oauth2_token = token

    resp = c.request("GET", "/me", api=True)


    assert resp["headers"].get("Authorization") == "Bearer ok"
  
    assert c.oauth2_token is token


def test_api_request_refreshes_when_dict_token_missing_expires_at():
    c = Client()
    c.oauth2_token = {"access_token": "no-expiry"}

    resp = c.request("GET", "/me", api=True)

    assert resp["headers"].get("Authorization") == "Bearer fresh-token"


def test_non_api_request_no_auth_header():
    c = Client()
    c.oauth2_token = OAuth2Token(access_token="should-not-be-used", expires_at=int(time.time()) + 3600)

    resp = c.request("GET", "/public", api=False)

    assert "Authorization" not in resp["headers"]


def test_api_request_preserves_existing_headers():
    c = Client()
    c.oauth2_token = OAuth2Token(access_token="ok", expires_at=int(time.time()) + 3600)
    custom_headers = {"X-Custom": "value"}

    resp = c.request("GET", "/me", api=True, headers=custom_headers)

    assert resp["headers"].get("Authorization") == "Bearer ok"
    assert resp["headers"].get("X-Custom") == "value"


def test_api_request_refreshes_when_token_expires_exactly_now():
    c = Client()
    current_time = int(time.time())
    c.oauth2_token = OAuth2Token(access_token="expired-now", expires_at=current_time)

    resp = c.request("GET", "/me", api=True)

    assert resp["headers"].get("Authorization") == "Bearer fresh-token"