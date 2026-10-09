"""Template logos: logo_url never points the server at arbitrary local files."""

import io

import pytest
from sqlmodel import Session

import api.it.templates
from models.it.templates import ITPdfTemplates


@pytest.fixture
def logo_dir(tmp_path, monkeypatch):
    directory = tmp_path / "logos"
    directory.mkdir()
    monkeypatch.setattr(api.it.templates, "LOGO_UPLOAD_DIR", directory)
    return directory


@pytest.fixture
def template(db_session: Session) -> ITPdfTemplates:
    row = ITPdfTemplates(tenant_id=1, name="Default", template_key="quotation_standard", company_name="PrimeFire")
    db_session.add(row)
    db_session.commit()
    db_session.refresh(row)
    return row


def test_create_rejects_local_logo_path(client, auth_headers, logo_dir) -> None:
    payload = {"name": "T", "template_key": "t", "company_name": "C", "logo_url": "../../main.py"}

    response = client.post("/it/templates/", json=payload, headers=auth_headers)

    assert response.status_code == 422


def test_update_rejects_new_local_logo_path(client, auth_headers, db_session, template, logo_dir) -> None:
    response = client.patch(
        f"/it/templates/{template.template_id}", json={"logo_url": "C:/Windows/win.ini"}, headers=auth_headers
    )

    assert response.status_code == 422
    db_session.refresh(template)
    assert template.logo_url is None


def test_update_accepts_external_https_logo(client, auth_headers, template, logo_dir) -> None:
    response = client.patch(
        f"/it/templates/{template.template_id}",
        json={"logo_url": "https://cdn.example.com/logo.png"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["logo_url"] == "https://cdn.example.com/logo.png"


def test_upload_serve_and_resave_uploaded_logo(client, auth_headers, template, logo_dir) -> None:
    """The SPA re-sends the stored local path when saving the form: that must keep working."""
    uploaded = client.post(
        f"/it/templates/{template.template_id}/logo",
        files={"logo_file": ("logo.png", io.BytesIO(b"\x89PNG-logo"), "image/png")},
        headers=auth_headers,
    )
    assert uploaded.status_code == 200
    stored = uploaded.json()["logo_url"]

    served = client.get(f"/it/templates/{template.template_id}/logo", headers=auth_headers)
    resaved = client.patch(
        f"/it/templates/{template.template_id}", json={"logo_url": stored, "name": "Renamed"}, headers=auth_headers
    )

    assert served.status_code == 200
    assert served.content == b"\x89PNG-logo"
    assert resaved.status_code == 200


def test_logo_outside_upload_dir_is_neither_served_nor_deleted(
    client, auth_headers, db_session, template, logo_dir, tmp_path
) -> None:
    outside = tmp_path / "secret.env"
    outside.write_text("SECRET=1")
    template.logo_url = str(outside)
    db_session.add(template)
    db_session.commit()

    served = client.get(f"/it/templates/{template.template_id}/logo", headers=auth_headers)
    replaced = client.post(
        f"/it/templates/{template.template_id}/logo",
        files={"logo_file": ("logo.png", io.BytesIO(b"\x89PNG"), "image/png")},
        headers=auth_headers,
    )

    assert served.status_code == 404
    assert "SECRET" not in served.text
    assert replaced.status_code == 200
    assert outside.exists()
