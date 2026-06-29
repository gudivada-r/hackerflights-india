import os
import json
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PROMPT_PATH = Path(__file__).parent / "prompts" / "intent_parser.txt"
BACKEND = os.getenv("MISTRAL_BACKEND", "ollama")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral-nemo")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "open-mistral-nemo")

def _load_system_prompt() -> str:
    raw = PROMPT_PATH.read_text(encoding="utf-8")
    return raw.replace("{{CURRENT_DATE}}", str(date.today()))

def _parse_json_response(text: str) -> dict:
    """Strip any accidental markdown fences and parse JSON."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1])
    return json.loads(text)

async def parse_intent(user_query: str) -> dict:
    system_prompt = _load_system_prompt()
    if BACKEND == "ollama":
        return await _call_ollama(system_prompt, user_query)
    else:
        return await _call_mistral_api(system_prompt, user_query)

async def _call_ollama(system_prompt: str, user_query: str) -> dict:
    import httpx
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        "stream": False,
        "format": "json"
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        content = data["message"]["content"]
        return _parse_json_response(content)

async def _call_mistral_api(system_prompt: str, user_query: str) -> dict:
    from mistralai import Mistral
    client = Mistral(api_key=MISTRAL_API_KEY)
    response = client.chat.complete(
        model=MISTRAL_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_query},
        ],
        response_format={"type": "json_object"},
    )
    return _parse_json_response(response.choices[0].message.content)
