import requests
from brain.adapters.base import BaseAIAdapter
from brain.context.assembler import ContextPackage

class OllamaAdapter(BaseAIAdapter):
    """
    Ollama connector inside the Execution Integration Layer.
    """
    @classmethod
    def execute(cls, pkg: ContextPackage, user_prompt: str, model: str = "llama3", host: str = "http://localhost:11434") -> str:
        """
        Executes query against local Ollama API instance. Falls back to mock if Ollama server is unreachable.
        """
        system_injection = cls.format_system_prompt(pkg, user_prompt)

        try:
            url = f"{host}/api/generate"
            data = {
                "model": model,
                "prompt": f"{system_injection}\n\nUser Prompt: {user_prompt}",
                "stream": False
            }
            resp = requests.post(url, json=data, timeout=5)
            if resp.status_code == 200:
                return resp.json()["response"]
        except Exception:
            pass

        return (
            f"[MOCK OLLAMA RESPONSE ({model} @ {host})]\n"
            f"Ollama server was not reachable. Fallback mock generated successfully.\n"
            f"Parsed project standard context for '{pkg.project}'."
        )
