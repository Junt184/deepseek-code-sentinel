from fastapi import APIRouter, HTTPException
from app.core.config import settings
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse
from app.services.llm_service import llm_service

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: AnalyzeRequest):
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=503, detail="DEEPSEEK_API_KEY not configured")

    result = await llm_service.analyze_code(request.code, request.language)

    status = "completed"
    if result.get("status") == "error":
        status = "failed"

    return AnalyzeResponse(
        status=status,
        vulnerabilities=result.get("vulnerabilities", []),
        summary=result.get("summary", "Analysis completed.")
    )
