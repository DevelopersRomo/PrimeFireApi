from unittest.mock import patch

import pytest
from starlette.requests import Request

from api.dependencies import get_request_app_url
from main import app

APP_URL = "https://app.primefire.us"


def _request(headers: dict[str, str]) -> Request:
    raw = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    return Request({"type": "http", "headers": raw, "app": app})


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        ({"Origin": "https://app.devromo.com"}, "https://app.devromo.com"),
        ({"Referer": "https://app.devromo.com/expenses/12"}, "https://app.devromo.com"),
        ({"Origin": "http://localhost:4200"}, "http://localhost:4200"),
        ({"Origin": "https://evil.example"}, APP_URL),
        ({"Referer": "https://evil.example/phish"}, APP_URL),
        ({"Origin": "https://app.devromo.com.evil.example"}, APP_URL),
        ({}, APP_URL),
    ],
)
def test_request_app_url_only_trusts_cors_origins(headers, expected):
    with patch("api.dependencies.settings.APP_URL", APP_URL):
        assert get_request_app_url(_request(headers)) == expected
