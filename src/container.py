from dotenv import load_dotenv
from fastapi import FastAPI
from openai import OpenAI
import os
from pydantic import BaseModel
from typing import Any
import uvicorn


class ExecRequest(BaseModel):
    input: str


def process_input(text: str) -> str:
    load_dotenv()
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    base_url = os.getenv("OPENAI_BASE_URL")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "OPENAI_API_KEY not set"

    try:
        client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
        resp = client.chat.completions.create(model=model, messages=[{"role": "user", "content": text}])
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


app = FastAPI()


@app.post("/exec")
async def exec_endpoint(req: ExecRequest) -> Any:
    output = process_input(req.input)
    return {"output": output}


@app.get("/health")
async def health() -> Any:
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
