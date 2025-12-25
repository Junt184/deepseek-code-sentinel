import re
from typing import Callable
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class CredentialScrubber:
    """
    Scrub sensitive credentials from code before sending to LLM.
    """
    SENSITIVE_PATTERNS = [
        r"(api_key|secret|password|token|access_key)\s*=\s*['\"][a-zA-Z0-9\-_]{8,}['\"]",
        r"(sk-[a-zA-Z0-9]{32,})",
        r"(ghp_[a-zA-Z0-9]{36})",
    ]

    @staticmethod
    def scrub(code: str) -> str:
        scrubbed_code = code
        for pattern in CredentialScrubber.SENSITIVE_PATTERNS:
            scrubbed_code = re.sub(pattern, r"\1='***SCRUBBED***'", scrubbed_code, flags=re.IGNORECASE)
        return scrubbed_code

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_content_length: int = 1024 * 10): # 10KB default
        super().__init__(app)
        self.max_content_length = max_content_length

    async def dispatch(self, request: Request, call_next: Callable):
        # 1. Input Size Validation
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.max_content_length:
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=413,
                content={"detail": "Payload too large. Max 10KB allowed."}
            )

        response = await call_next(request)
        return response
