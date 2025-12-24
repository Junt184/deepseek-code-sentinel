from pydantic import BaseModel, Field
from typing import List
from enum import Enum

class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class AnalyzeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=10000, description="Source code to analyze (max 10KB)")
    language: str = Field(..., description="Programming language of the code")
    stream: bool = Field(default=True, description="Whether to stream the response")

class Vulnerability(BaseModel):
    severity: Severity
    line: int
    description: str
    suggestion: str

class AnalyzeResponse(BaseModel):
    status: str
    vulnerabilities: List[Vulnerability] = []
    summary: str
