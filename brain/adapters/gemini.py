import os
import requests
from brain.adapters.base import BaseAIAdapter
from brain.context.assembler import ContextPackage

class GeminiAdapter(BaseAIAdapter):
    @classmethod
    def execute(cls, pkg: ContextPackage, user_prompt: str, model: str = "gemini-1.5-pro") -> str:
        """
        Executes query against Google Gemini API. Falls back to mock if key is missing.
        """
        api_key = os.environ.get("GEMINI_API_KEY")
        system_injection = cls.format_system_prompt(pkg, user_prompt)

        if not api_key:
            return (
                f"[MOCK GEMINI RESPONSE ({model})]\n"
                f"Successfully parsed standard context for project '{pkg.project}'.\n"
                f"We injected {len(pkg.related_docs)} documents to shape the output.\n"
                f"Received User Prompt: '{user_prompt}'"
            )

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            headers = {
                "Content-Type": "application/json"
            }
            combined_text = f"{system_injection}\n\nUser Question: {user_prompt}"
            data = {
                "contents": [{
                    "parts": [{"text": combined_text}]
                }]
            }
            resp = requests.post(url, json=data, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return f"Gemini API Error: {resp.status_code} - {resp.text}"
        except Exception as e:
            return f"Gemini execution exception: {str(e)}"
