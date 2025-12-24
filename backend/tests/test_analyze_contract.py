from fastapi.testclient import TestClient

import app.services.llm_service as llm_module
from main import app


def test_analyze_contract(monkeypatch) -> None:
    async def fake_analyze_code(code: str, language: str):
        return {
            "vulnerabilities": [
                {
                    "severity": "high",
                    "line": 1,
                    "description": "test",
                    "suggestion": "fix",
                }
            ],
            "summary": "ok",
        }

    monkeypatch.setattr(llm_module.llm_service, "analyze_code", fake_analyze_code)

    client = TestClient(app)
    response = client.post(
        "/api/v1/analyze",
        json={"code": "print('x')", "language": "python", "stream": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["summary"] == "ok"
    assert len(body["vulnerabilities"]) == 1
    assert body["vulnerabilities"][0]["severity"] == "high"


def test_analyze_rejects_blank_code() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/analyze",
        json={"code": "   ", "language": "python"},
    )
    assert response.status_code == 400

