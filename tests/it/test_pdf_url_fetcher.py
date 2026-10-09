"""The PDF renderer may only fetch template assets, uploaded logos and public https images."""

import pathlib
import socket

import pytest

import api.it.templates
from services.it import pdf_service
from services.it.pdf_service import TEMPLATES_DIR, safe_url_fetcher

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


@pytest.fixture
def logo_dir(tmp_path, monkeypatch):
    directory = tmp_path / "logos"
    directory.mkdir()
    monkeypatch.setattr(api.it.templates, "LOGO_UPLOAD_DIR", directory)
    return directory


def _public_dns(monkeypatch, ip: str = "93.184.216.34") -> None:
    monkeypatch.setattr(socket, "getaddrinfo", lambda *_a, **_k: [(socket.AF_INET, 0, 0, "", (ip, 0))])


class _FakeResponse:
    def __init__(self, status_code: int, content: bytes = b"", headers: dict | None = None) -> None:
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}


def test_template_assets_are_allowed() -> None:
    result = safe_url_fetcher((TEMPLATES_DIR / "quotation_standard.css").as_uri())

    body = result.get("string") or result["file_obj"].read()
    assert body


def test_uploaded_logo_is_allowed(logo_dir) -> None:
    logo = logo_dir / "logo.png"
    logo.write_bytes(b"\x89PNG")

    result = safe_url_fetcher(logo.as_uri())

    body = result.get("string") or result["file_obj"].read()
    assert body == b"\x89PNG"


@pytest.mark.parametrize("target", ["main.py", "core/config.py"])
def test_local_files_outside_allowed_dirs_are_refused(logo_dir, target) -> None:
    with pytest.raises(ValueError, match="outside the template and logo folders"):
        safe_url_fetcher((REPO_ROOT / target).as_uri())


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/admin",
        "http://localhost:8000/backups/status",
        "http://169.254.169.254/latest/meta-data/",
        "http://10.0.0.5/internal.png",
        "ftp://example.com/logo.png",
    ],
)
def test_internal_and_unsupported_urls_are_refused(url) -> None:
    with pytest.raises(ValueError, match=r"non-public address|Unsupported URL scheme"):
        safe_url_fetcher(url)


def test_public_https_logo_is_fetched_without_following_redirects(monkeypatch) -> None:
    _public_dns(monkeypatch)
    calls = []

    def fake_get(url, **kwargs):
        calls.append(kwargs)
        return _FakeResponse(200, b"\x89PNG-remote", {"content-type": "image/png"})

    monkeypatch.setattr(pdf_service.httpx, "get", fake_get)

    result = safe_url_fetcher("https://cdn.example.com/logo.png")

    assert result["string"] == b"\x89PNG-remote"
    assert result["mime_type"] == "image/png"
    assert calls[0]["follow_redirects"] is False


def test_public_url_redirect_is_refused(monkeypatch) -> None:
    _public_dns(monkeypatch)
    monkeypatch.setattr(
        pdf_service.httpx,
        "get",
        lambda _url, **_k: _FakeResponse(302, headers={"location": "http://169.254.169.254/"}),
    )

    with pytest.raises(ValueError, match="HTTP 302"):
        safe_url_fetcher("https://cdn.example.com/logo.png")


def test_generate_quotation_pdf_uses_the_safe_fetcher(monkeypatch) -> None:
    import weasyprint

    captured = {}

    class _StopRenderError(Exception):
        pass

    class _FakeHTML:
        def __init__(self, **kwargs) -> None:
            captured.update(kwargs)
            raise _StopRenderError

    monkeypatch.setattr(weasyprint, "HTML", _FakeHTML)
    monkeypatch.setattr(pdf_service, "render_quotation_html", lambda *_a, **_k: "<html></html>")

    with pytest.raises(_StopRenderError):
        pdf_service.generate_quotation_pdf(db=None, quotation=None)

    assert captured.get("url_fetcher") is safe_url_fetcher
