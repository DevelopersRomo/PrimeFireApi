from datetime import timedelta
from io import BytesIO

import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlmodel import Session

import api.home_posts as home_posts_api
from api.dependencies import (
    get_current_employee,
    get_current_employee_with_permissions,
    require_authentication,
)
from core.datetime_utils import utcnow
from main import app
from models.employees import Employees
from models.home_posts import HomePost

BASE = "/api/v1/home-posts"
ALL_ACTIONS = ("can_view", "can_create", "can_edit", "can_delete")


@pytest.fixture(autouse=True)
def upload_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(home_posts_api, "UPLOAD_DIR", tmp_path / "home_posts")
    return tmp_path / "home_posts"


@pytest.fixture
def author(db_session: Session) -> Employees:
    emp = Employees(email="author@example.com", first_name="Ada", last_name="Lovelace")
    db_session.add(emp)
    db_session.commit()
    db_session.refresh(emp)
    return emp


@pytest.fixture
def act_as():
    def _act(employee: Employees, *actions: str):
        perms = {"permissions": [{"module_key": "home_posts", "permissions": dict.fromkeys(actions, True)}]}
        app.dependency_overrides[get_current_employee] = lambda: employee
        app.dependency_overrides[get_current_employee_with_permissions] = lambda: perms
        app.dependency_overrides[require_authentication] = lambda: {"sub": employee.email}

    yield _act
    app.dependency_overrides.pop(get_current_employee, None)
    app.dependency_overrides.pop(get_current_employee_with_permissions, None)
    app.dependency_overrides.pop(require_authentication, None)


def _post(db: Session, title: str, **fields) -> HomePost:
    now = utcnow()
    values = {"post_type": "news", "body_html": "<p>Body</p>", "published_at": now - timedelta(hours=1)}
    values.update(fields)
    post = HomePost(title=title, created_at=now, updated_at=now, **values)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def _payload(**overrides) -> dict:
    payload = {"title": "Town hall", "post_type": "news", "body_html": "<p>Hello team</p>"}
    payload.update(overrides)
    return payload


def _png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (4, 4), "red").save(buffer, format="PNG")
    return buffer.getvalue()


# --- feed ------------------------------------------------------------------


def test_feed_shows_only_visible_posts_pinned_first(act_as, client: TestClient, db_session: Session, author):
    now = utcnow()
    _post(db_session, "Older", published_at=now - timedelta(days=2), created_by=author.employee_id)
    _post(db_session, "Newer", published_at=now - timedelta(hours=1))
    _post(db_session, "Pinned", published_at=now - timedelta(days=5), is_pinned=True)
    _post(db_session, "Draft", published_at=None)
    _post(db_session, "Scheduled", published_at=now + timedelta(days=1))
    _post(db_session, "Expired", expires_at=now - timedelta(minutes=1))
    _post(db_session, "Deleted", is_active=False)
    _post(db_session, "Expires later", published_at=now - timedelta(days=3), expires_at=now + timedelta(days=1))

    act_as(author)
    response = client.get(f"{BASE}/feed")

    assert response.status_code == 200
    body = response.json()
    assert [item["title"] for item in body["items"]] == ["Pinned", "Newer", "Older", "Expires later"]
    assert body["total"] == 4
    assert body["has_more"] is False
    older = body["items"][2]
    assert older["author_name"] == "Ada Lovelace"
    assert older["status"] == "published"
    assert older["has_cover"] is False
    assert older["published_at"].endswith("Z")


def test_feed_paginates_and_filters_by_type(act_as, client: TestClient, db_session: Session, author):
    now = utcnow()
    for i in range(3):
        _post(db_session, f"News {i}", published_at=now - timedelta(hours=i + 1))
    _post(db_session, "Party", post_type="event", event_at=now + timedelta(days=3))

    act_as(author)
    page = client.get(f"{BASE}/feed", params={"skip": 0, "limit": 2}).json()
    assert page["total"] == 4
    assert len(page["items"]) == 2
    assert page["has_more"] is True

    events = client.get(f"{BASE}/feed", params={"post_type": "event"}).json()
    assert [item["title"] for item in events["items"]] == ["Party"]


# --- sanitization and validation -------------------------------------------


def test_create_sanitizes_body_html(act_as, client: TestClient, author):
    act_as(author, "can_create")
    dirty = (
        '<p class="ql-align-center evil">Hi <strong>bold</strong> <em>it</em></p>'
        "<script>alert(1)</script>"
        '<img src="x" onerror="alert(1)">'
        '<a href="javascript:alert(1)">bad</a>'
        '<a href="https://example.com" onclick="steal()">good</a>'
        '<ol><li data-list="bullet" class="ql-indent-1">item</li></ol>'
        '<iframe src="https://evil"></iframe><style>p{}</style>'
    )
    response = client.post(BASE, json=_payload(body_html=dirty, published_at=utcnow().isoformat() + "Z"))

    assert response.status_code == 201
    html = response.json()["body_html"]
    for forbidden in ("<script", "alert(1)", "onerror", "onclick", "javascript:", "<img", "<iframe", "<style", "evil"):
        assert forbidden not in html
    assert '<p class="ql-align-center">' in html
    assert "<strong>bold</strong>" in html
    assert "<em>it</em>" in html
    assert 'href="https://example.com"' in html
    assert 'target="_blank"' in html
    assert 'rel="noopener noreferrer"' in html
    assert '<li data-list="bullet" class="ql-indent-1">item</li>' in html


def test_create_rejects_body_empty_after_sanitizing(act_as, client: TestClient, author):
    act_as(author, "can_create")
    response = client.post(BASE, json=_payload(body_html="<p><br></p><script>alert(1)</script><p> &nbsp; </p>"))
    assert response.status_code == 422


def test_event_requires_event_at(act_as, client: TestClient, author):
    act_as(author, "can_create")
    assert client.post(BASE, json=_payload(post_type="event")).status_code == 422


def test_expires_must_be_after_published(act_as, client: TestClient, author):
    act_as(author, "can_create")
    response = client.post(
        BASE,
        json=_payload(published_at="2030-01-02T00:00:00Z", expires_at="2030-01-01T00:00:00Z"),
    )
    assert response.status_code == 422


def test_blank_title_rejected(act_as, client: TestClient, author):
    act_as(author, "can_create")
    assert client.post(BASE, json=_payload(title="   ")).status_code == 422


def test_news_drops_event_fields_and_dates_are_stored_as_utc(act_as, client: TestClient, db_session: Session, author):
    act_as(author, "can_create")
    response = client.post(
        BASE,
        json=_payload(
            title="  Spaced  ",
            event_at="2030-05-01T10:00:00Z",
            location="Room 1",
            published_at="2030-01-01T10:00:00+02:00",
        ),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Spaced"
    assert body["event_at"] is None
    assert body["location"] is None
    assert body["published_at"] == "2030-01-01T08:00:00Z"
    assert body["status"] == "scheduled"
    assert body["created_by"] == author.employee_id
    stored = db_session.get(HomePost, body["post_id"])
    assert stored.published_at.tzinfo is None
    assert stored.published_at.hour == 8


def test_event_keeps_event_fields(act_as, client: TestClient, author):
    act_as(author, "can_create")
    response = client.post(
        BASE, json=_payload(post_type="event", event_at="2030-05-01T10:00:00Z", location="Main office")
    )
    assert response.status_code == 201
    assert response.json()["event_at"] == "2030-05-01T10:00:00Z"
    assert response.json()["location"] == "Main office"
    assert response.json()["status"] == "draft"


def test_update_and_soft_delete(act_as, client: TestClient, db_session: Session, author):
    post = _post(db_session, "Original")
    act_as(author, *ALL_ACTIONS)

    updated = client.put(f"{BASE}/{post.post_id}", json=_payload(title="Changed", body_html="<p>New <b>x</b></p>"))
    assert updated.status_code == 200
    assert updated.json()["title"] == "Changed"

    assert client.delete(f"{BASE}/{post.post_id}").status_code == 204
    db_session.expire_all()
    assert db_session.get(HomePost, post.post_id).is_active is False
    assert client.get(f"{BASE}/feed").json()["total"] == 0
    assert client.put(f"{BASE}/{post.post_id}", json=_payload()).status_code == 404


# --- permissions and visibility --------------------------------------------


def test_admin_endpoints_require_module_permission(act_as, client: TestClient, db_session: Session, author):
    post = _post(db_session, "Locked")
    act_as(author)

    assert client.get(BASE).status_code == 403
    assert client.post(BASE, json=_payload()).status_code == 403
    assert client.put(f"{BASE}/{post.post_id}", json=_payload()).status_code == 403
    assert client.delete(f"{BASE}/{post.post_id}").status_code == 403
    files = {"file": ("c.png", _png_bytes(), "image/png")}
    assert client.post(f"{BASE}/{post.post_id}/cover", files=files).status_code == 403
    assert client.delete(f"{BASE}/{post.post_id}/cover").status_code == 403


def test_detail_visibility(act_as, client: TestClient, db_session: Session, author):
    visible = _post(db_session, "Visible")
    draft = _post(db_session, "Draft", published_at=None)
    deleted = _post(db_session, "Deleted", is_active=False)

    act_as(author)
    assert client.get(f"{BASE}/{visible.post_id}").status_code == 200
    assert client.get(f"{BASE}/{draft.post_id}").status_code == 404

    act_as(author, "can_view")
    response = client.get(f"{BASE}/{draft.post_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "draft"
    assert client.get(f"{BASE}/{deleted.post_id}").status_code == 404


def test_admin_list_filters_by_derived_status(act_as, client: TestClient, db_session: Session, author):
    now = utcnow()
    _post(db_session, "Draft", published_at=None)
    _post(db_session, "Scheduled", published_at=now + timedelta(days=1))
    _post(db_session, "Published", is_pinned=True)
    _post(db_session, "Expired", expires_at=now - timedelta(minutes=1))
    _post(db_session, "Deleted", is_active=False)

    act_as(author, "can_view")
    everything = client.get(BASE).json()
    assert {item["title"]: item["status"] for item in everything} == {
        "Draft": "draft",
        "Scheduled": "scheduled",
        "Published": "published",
        "Expired": "expired",
    }
    assert everything[0]["title"] == "Published"

    for status in ("draft", "scheduled", "published", "expired"):
        page = client.get(BASE, params={"status": status, "with_meta": True}).json()
        assert [item["status"] for item in page["items"]] == [status]
        assert page["total"] == 1

    assert [item["title"] for item in client.get(BASE, params={"search": "sched"}).json()] == ["Scheduled"]


# --- cover -----------------------------------------------------------------


def test_cover_upload_and_download(act_as, client: TestClient, db_session: Session, author, upload_dir):
    post = _post(db_session, "With cover")
    png = _png_bytes()

    act_as(author, "can_edit")
    response = client.post(f"{BASE}/{post.post_id}/cover", files={"file": ("cover.png", png, "image/png")})
    assert response.status_code == 200
    assert response.json()["has_cover"] is True
    first_files = list(upload_dir.rglob("*.*"))
    assert len(first_files) == 1

    replaced = client.post(f"{BASE}/{post.post_id}/cover", files={"file": ("new.png", png, "image/png")})
    assert replaced.status_code == 200
    assert not first_files[0].exists()

    act_as(author)
    served = client.get(f"{BASE}/{post.post_id}/cover")
    assert served.status_code == 200
    assert served.headers["content-type"] == "image/png"
    assert served.content == png

    act_as(author, "can_edit")
    assert client.delete(f"{BASE}/{post.post_id}/cover").status_code == 204
    assert list(upload_dir.rglob("*.*")) == []
    assert client.get(f"{BASE}/{post.post_id}/cover").status_code == 404


def test_cover_rejects_non_images_and_large_files(act_as, client: TestClient, db_session: Session, author):
    post = _post(db_session, "Cover rules")
    act_as(author, "can_edit")

    fake = client.post(
        f"{BASE}/{post.post_id}/cover", files={"file": ("cover.png", b"<html>not an image</html>", "image/png")}
    )
    assert fake.status_code == 422

    big = _png_bytes() + b"\0" * (5 * 1024 * 1024)
    assert client.post(f"{BASE}/{post.post_id}/cover", files={"file": ("big.png", big, "image/png")}).status_code == 413


def test_cover_of_draft_hidden_from_regular_users(act_as, client: TestClient, db_session: Session, author):
    draft = _post(db_session, "Draft", published_at=None)
    act_as(author, "can_edit")
    files = {"file": ("cover.png", _png_bytes(), "image/png")}
    assert client.post(f"{BASE}/{draft.post_id}/cover", files=files).status_code == 200

    act_as(author)
    assert client.get(f"{BASE}/{draft.post_id}/cover").status_code == 404
