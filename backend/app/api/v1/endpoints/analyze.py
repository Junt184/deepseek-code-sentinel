from fastapi import APIRouter, HTTPException
from app.schemas.analyze import AnalyzeRequest, AnalyzeResponse, Vulnerability, Severity

router = APIRouter()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_code(request: AnalyzeRequest):
    """
    Mock endpoint for code analysis.
    This will be replaced by actual DeepSeek API call in Phase 2.
    """
    if not request.code.strip():
        raise HTTPException(status_code=400, detail="Code cannot be empty")

    # Mock response for infrastructure testing
    mock_vulns = [
        Vulnerability(
            severity=Severity.HIGH,
            line=42,
            description="Potential SQL Injection detected in user input handling.",
            suggestion="Use parameterized queries instead of string concatenation."
        ),
        Vulnerability(
            severity=Severity.MEDIUM,
            line=15,
            description="Hardcoded secret key found.",
            suggestion="Use environment variables for secrets."
        )
    ]

    return AnalyzeResponse(
        status="completed",
        vulnerabilities=mock_vulns,
        summary=f"Analysis completed for {request.language} code. Found {len(mock_vulns)} issues."
    )
