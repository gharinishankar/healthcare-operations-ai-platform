
import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL = "qwen2.5:3b"


def generate_investigation_ideas(verified_summary):
    prompt = f"""
You are a healthcare operations assistant analysing
synthetic GP appointment data.

IMPORTANT:
DNA means Did Not Attend, not genetic DNA.

VERIFIED STATISTICS:
{verified_summary}

TASK:
Suggest exactly two practical areas to investigate
to better understand missed appointments.

RULES:
- Do not repeat or recalculate statistics.
- Do not invent causes for missed appointments.
- Use neutral, non-judgemental language.
- Present suggestions as possibilities, not proven facts.
- Keep your response under 80 words.
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2}
    }

    request = Request(
        OLLAMA_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urlopen(request, timeout=120) as response:
        result = json.load(response)

    return result["response"].strip()
