"""Bound request bodies even when Transfer-Encoding omits Content-Length."""
from fastapi.responses import JSONResponse
from app.core.config import settings


class BodyLimitExceeded(Exception):
    pass


class RequestBodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        consumed = 0
        exceeded = False
        replied = False

        async def bounded_receive():
            nonlocal consumed, exceeded
            message = await receive()
            if message["type"] == "http.request":
                consumed += len(message.get("body", b""))
                if consumed > (settings.MAX_FILE_SIZE_MB + 1) * 1024 * 1024:
                    exceeded = True
                    raise BodyLimitExceeded()
            return message

        async def bounded_send(message):
            nonlocal replied
            if exceeded:
                if not replied:
                    replied = True
                    response = JSONResponse({"detail": "Request body exceeds upload limit."}, status_code=413, headers={"Cache-Control": "no-store"})
                    await response(scope, receive, send)
                return
            await send(message)

        try:
            await self.app(scope, bounded_receive, bounded_send)
        except BodyLimitExceeded:
            if not replied:
                await bounded_send({"type": "http.response.start"})
