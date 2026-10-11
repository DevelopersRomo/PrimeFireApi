"""Reject oversized request bodies before the framework buffers them, authentication included."""

from starlette.types import ASGIApp, Message, Receive, Scope, Send

JSON_BODY_LIMIT = 8 * 1024 * 1024  # contact submissions carry base64 attachments (~5.4 MB)
UPLOAD_BODY_LIMIT = 30 * 1024 * 1024  # largest upload is 25 MiB (agreements) plus multipart framing


class _BodyTooLargeError(Exception):
    pass


class BodyLimitMiddleware:
    """Cap request bodies by Content-Length up front and by streamed byte count, with a larger multipart allowance."""

    def __init__(
        self, app: ASGIApp, default_limit: int = JSON_BODY_LIMIT, upload_limit: int = UPLOAD_BODY_LIMIT
    ) -> None:
        self.app = app
        self.default_limit = default_limit
        self.upload_limit = upload_limit

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        is_upload = headers.get(b"content-type", b"").lower().startswith(b"multipart/")
        limit = self.upload_limit if is_upload else self.default_limit

        declared = headers.get(b"content-length", b"")
        if declared.isdigit() and int(declared) > limit:
            await self._reject(send)
            return

        received = 0
        response_started = False

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > limit:
                    raise _BodyTooLargeError
            return message

        async def tracking_send(message: Message) -> None:
            nonlocal response_started
            response_started = response_started or message["type"] == "http.response.start"
            await send(message)

        try:
            await self.app(scope, limited_receive, tracking_send)
        except _BodyTooLargeError:
            if not response_started:
                await self._reject(send)

    @staticmethod
    async def _reject(send: Send) -> None:
        body = b'{"detail":"Request body too large"}'
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())],
            }
        )
        await send({"type": "http.response.body", "body": body})
