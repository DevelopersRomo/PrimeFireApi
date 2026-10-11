from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from core.body_limit import JSON_BODY_LIMIT, UPLOAD_BODY_LIMIT, BodyLimitMiddleware


def _app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(BodyLimitMiddleware, default_limit=100, upload_limit=1000)

    @app.post("/echo")
    async def echo(request: Request):
        return {"size": len(await request.body())}

    return app


def test_body_within_the_limit_passes():
    response = TestClient(_app()).post("/echo", content=b"x" * 100)

    assert response.status_code == 200
    assert response.json() == {"size": 100}


def test_declared_oversize_body_is_rejected_with_413():
    response = TestClient(_app()).post("/echo", content=b"x" * 101)

    assert response.status_code == 413
    assert response.json() == {"detail": "Request body too large"}


def test_streamed_body_without_content_length_is_cut_off_at_the_limit():
    def chunks():
        for _ in range(11):
            yield b"x" * 10

    response = TestClient(_app()).post("/echo", content=chunks())

    assert response.status_code == 413


def test_multipart_uploads_get_the_larger_allowance():
    response = TestClient(_app()).post("/echo", files={"file": ("a.bin", b"x" * 500)})

    assert response.status_code == 200


def test_multipart_uploads_are_still_capped():
    response = TestClient(_app()).post("/echo", files={"file": ("a.bin", b"x" * 1500)})

    assert response.status_code == 413


def test_the_real_app_rejects_an_oversized_body_before_authentication(client: TestClient):
    response = client.post("/auth/token", content=b"x" * (JSON_BODY_LIMIT + 1))

    assert response.status_code == 413


def test_the_upload_allowance_covers_the_largest_known_upload():
    # agreements accept 25 MiB files; the multipart envelope adds a little on top
    assert UPLOAD_BODY_LIMIT > 25 * 1024 * 1024
