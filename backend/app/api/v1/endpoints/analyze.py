from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from app.core.config import settings
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.llm_service import llm_service
from app.core.rate_limiter import rate_limiter
from app.middleware.security import CredentialScrubber

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: Request, body: AnalyzeRequest):
    # 1. Rate Limiting
    client_ip = request.client.host if request.client else "unknown"
    rate_limiter.check(client_ip)

    if not body.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=503, detail="DEEPSEEK_API_KEY not configured")

    # 2. Credential Scrubbing
    safe_code = CredentialScrubber.scrub(body.code)

    if body.stream:
        return StreamingResponse(
            llm_service.analyze_code_stream(safe_code, body.language),
            media_type="text/event-stream"
        )

    result = await llm_service.analyze_code(safe_code, body.language)

    status = "completed"
    if result.get("status") == "error":
        status = "failed"

    return AnalyzeResponse(
        status=status,
        vulnerabilities=result.get("vulnerabilities", []),
        summary=result.get("summary", "Analysis completed.")
    )
