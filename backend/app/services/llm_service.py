import json
from typing import Any, Dict

from openai import AsyncOpenAI

from app.core.config import settings

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_URL
        )

    def _build_prompt(self, code: str, language: str) -> str:
        return f"""
你是一名严谨的代码安全审计专家。请分析下面这段 {language} 代码的安全风险。

输出语言要求：
除 severity 字段外，其余字段（description、suggestion、summary）必须使用中文。

Output Format:
You MUST output a valid JSON object. Do not include any markdown formatting (like ```json).
The JSON structure must be:
{{
    "vulnerabilities": [
        {{
            "severity": "high|medium|low|info",
            "line": <line_number>,
            "description": "<中文问题描述>",
            "suggestion": "<中文修复建议>"
        }}
    ],
    "summary": "<中文总结>"
}}

Code to Analyze:
{code}
"""

    async def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Non-streaming analysis (returns complete JSON)
        """
        try:
            response = await self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一名严谨的代码安全审计专家。必须输出 JSON 对象，且 description、suggestion、summary 使用中文。"},
                    {"role": "user", "content": self._build_prompt(code, language)}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            # Fallback error handling
            return {
                "status": "error",
                "summary": f"LLM Analysis Failed: {str(e)}",
                "vulnerabilities": []
            }

llm_service = LLMService()
