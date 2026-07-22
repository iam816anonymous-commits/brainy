import os
import requests
from brain.adapters.base import BaseAIAdapter
from brain.context.assembler import ContextPackage

class ClaudeAdapter(BaseAIAdapter):
    @classmethod
    def execute(cls, pkg: ContextPackage, user_prompt: str, model: str = "claude-3-5-sonnet-20241022") -> str:
        """
        Executes query against Anthropic Claude API. Falls back to mock if key is missing.
        """
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        system_injection = cls.format_system_prompt(pkg, user_prompt)

        if not api_key:
            return (
                f"[MOCK CLAUDE RESPONSE ({model})]\n"
                f"Successfully parsed standard context for project '{pkg.project}'.\n"
                f"Incorporating instructions from active task: {pkg.current_task or 'None'}.\n"
                f"Decisions enforced: {', '.join(d['title'] for d in pkg.decisions) or 'None'}.\n"
                f"Received User Prompt: '{user_prompt}'"
            )

        try:
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "system": system_injection,
                "messages": [
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 1024
            }
            resp = requests.post(url, json=data, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()["content"][0]["text"]
            else:
                return f"Claude API Error: {resp.status_code} - {resp.text}"
        except Exception as e:
            return f"Claude execution exception: {str(e)}"
