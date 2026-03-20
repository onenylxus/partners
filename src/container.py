# File: container.py
# Summary: Exposes a FastAPI service that processes user input with the OpenAI client.

from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
import os
import json
from pydantic import BaseModel
from typing import Any
import uvicorn


class ExecRequest(BaseModel):
    input: str
    system: str | None = None


class RouteCandidate(BaseModel):
    name: str
    brief: str = ""


class RouteRequest(BaseModel):
    input: str
    candidates: list[RouteCandidate]


def process_input(text: str, system: str | None = None) -> str:
    load_dotenv()

    model = os.getenv("OPENAI_MODEL")
    if not model:
        return "OPENAI_MODEL not set"

    base_url = os.getenv("OPENAI_BASE_URL")
    if not base_url:
        return "OPENAI_BASE_URL not set"

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY not set"

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        messages = []
        if system and system.strip():
            messages.append({"role": "system", "content": system.strip()})
        messages.append({"role": "user", "content": text})
        resp = client.chat.completions.create(model=model, messages=messages)
        # Try common access patterns for the response content
        try:
            return resp.choices[0].message.content
        except Exception:
            try:
                return resp.choices[0].message["content"]
            except Exception:
                return str(resp)
    except Exception as e:
        return str(e)


def route_prompt(text: str, candidates: list[RouteCandidate]) -> tuple[str, str]:
    """Ask the model to choose the best candidate container name."""
    candidate_names = [c.name for c in candidates]
    if not candidates:
        return "", "No candidates provided"

    instruction = (
        "You are a routing coordinator. Choose exactly one best container name "
        "from the candidates for the user prompt. Return strict JSON with keys "
        "target and reason. target must be one of the candidates exactly."
    )

    candidate_lines = []
    for c in candidates:
        if c.brief.strip():
            candidate_lines.append(f"- {c.name}: {c.brief.strip()}")
        else:
            candidate_lines.append(f"- {c.name}")

    prompt = (
        "Candidates:\n" + "\n".join(candidate_lines) + "\n"
        f"User prompt: {text}\n"
        "Respond with JSON only."
    )

    raw = process_input(f"{instruction}\n\n{prompt}")

    # First try strict JSON parsing.
    try:
        obj = json.loads(raw)
        target = str(obj.get("target", "")).strip()
        reason = str(obj.get("reason", "")).strip()
        if target in candidate_names:
            return target, reason or "model-selected"
    except Exception:
        pass

    # Fallback: attempt to find one candidate name in plain text response.
    lowered = (raw or "").lower()
    for name in candidate_names:
        if name.lower() in lowered:
            return name, "parsed from plain-text response"

    return candidate_names[0], "fallback to first candidate"


app = FastAPI()


@app.post("/exec")
async def exec_endpoint(req: ExecRequest) -> Any:
    output = process_input(req.input, req.system)
    return {"output": output}


@app.post("/route")
async def route_endpoint(req: RouteRequest) -> Any:
    target, reason = route_prompt(req.input, req.candidates)
    return {"target": target, "reason": reason}


@app.get("/health")
async def health() -> Any:
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
