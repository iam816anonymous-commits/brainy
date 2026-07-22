import os
import requests
from brain.adapters.base import BaseAIAdapter
from brain.context.assembler import ContextPackage

class ChatGPTAdapter(BaseAIAdapter):
    @classmethod
    def execute(cls, pkg: ContextPackage, user_prompt: str, model: str = "gpt-4o") -> str:
        """
        Executes query against ChatGPT/OpenAI API. Falls back to mock if key is missing.
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        system_injection = cls.format_system_prompt(pkg, user_prompt)

        if not api_key:
            # Deterministic, high-fidelity mock response showing prompt assembly
            return (
                f"[MOCK CHATGPT RESPONSE ({model})]\n"
                f"Successfully parsed standard context for project '{pkg.project}'.\n"
                f"We analyzed {len(pkg.relevant_code)} code blocks, {len(pkg.decisions)} decisions, and {len(pkg.known_failures)} failures.\n"
                f"Avoiding failures: {', '.join(f['title'] for f in pkg.known_failures) or 'None'}.\n"
                f"Received User Prompt: '{user_prompt}'"
            )

        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_injection},
                    {"role": "user", "content": user_prompt}
                ]
            }
            resp = requests.post(url, json=data, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            else:
                return f"ChatGPT API Error: {resp.status_code} - {resp.text}"
        except Exception as e:
            return f"ChatGPT execution exception: {str(e)}"
