import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.request_id = rid = str(uuid.uuid4())
        response = await call_next(request)
        response.headers["X-Request-ID"] = rid
        return response
