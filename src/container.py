import os
import sys
import uvicorn
from typing import Any
from fastapi import FastAPI
from pydantic import BaseModel


class ExecRequest(BaseModel):
    input: str


def process_input(text: str) -> str:
    """Process the input text and return the resulting output.

    Current behavior mirrors the previous stdin->stdout echo behavior.
    Replace or extend this function to add more complex logic.
    """
    # Keep behavior simple: echo the provided text
    return text


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
