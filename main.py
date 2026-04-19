# -*- coding: utf-8 -*-
"""
PathoScan — FastAPI Backend
Serves the fine-tuned Gemma 4 E4B model via Ollama for offline skin lesion triage.
"""

import json
import base64
import httpx
import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from pydantic import BaseModel
from typing import Optional
from PIL import Image
import io

app = FastAPI(
    title="PathoScan API",
    description="Offline AI skin lesion triage powered by Gemma 4 E4B",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # localhost only in production
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL  = "http://localhost:11435"
MODEL_NAME  = "pathoscan-gemma4"   # matches Modelfile

SYSTEM_PROMPT = """You are PathoScan, an AI dermatology assistant for community health workers.
Analyze the skin lesion image and respond ONLY with a valid JSON object:
{
  "condition": "<condition name>",
  "condition_code": "<code>",
  "severity": "LOW|MEDIUM|HIGH",
  "confidence": "<XX%>",
  "description": "<clinical description>",
  "urgency": "<timeframe>",
  "recommended_action": "<next steps>",
  "visual_features": ["<feature1>", "<feature2>"],
  "disclaimer": "This is an AI-assisted screening tool. Always consult a qualified healthcare professional."
}"""


class TriageResponse(BaseModel):
    condition: str
    condition_code: str
    severity: str
    confidence: str
    description: str
    urgency: str
    recommended_action: str
    visual_features: list[str]
    disclaimer: str


def preprocess_image(image_bytes: bytes, max_size: int = 512) -> str:
    """Resize image and convert to base64 for Ollama."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Resize keeping aspect ratio
    img.thumbnail((max_size, max_size), Image.LANCZOS)

    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the web interface."""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>PathoScan API</h1><p>Visit /docs for API documentation</p>"


@app.get("/health")
async def health_check():
    """Check if Ollama is running and the model is loaded."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            models = [m["name"] for m in r.json().get("models", [])]
            model_ready = any(MODEL_NAME in m for m in models)
        return {
            "status": "ok",
            "ollama": "running",
            "model_loaded": model_ready,
            "model_name": MODEL_NAME,
            "offline_capable": True
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/analyze", response_model=TriageResponse)
async def analyze_lesion(file: UploadFile = File(...)):
    """
    Analyze a skin lesion image and return structured triage output.
    Runs fully offline via local Ollama instance.
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    image_bytes = await file.read()

    # Enforce max size (10MB)
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large. Max 10MB.")

    image_b64 = preprocess_image(image_bytes)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": "Analyze this skin lesion image and provide a triage assessment.",
                "images": [image_b64]
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.1,     # low temp = consistent structured output
            "top_p": 0.9,
            "num_predict": 512,
        }
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json=payload
            )
            response.raise_for_status()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Ollama not running. Start it with: ollama serve"
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Model inference timed out.")

    raw = response.json()["message"]["content"].strip()

    # Clean up response — remove markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from response
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            raise HTTPException(
                status_code=500,
                detail="Model returned invalid JSON. Try again."
            )

    # Ensure all required fields are present
    result.setdefault("visual_features", [])
    result.setdefault("disclaimer",
        "This is an AI-assisted screening tool. Always consult a qualified healthcare professional.")

    return TriageResponse(**result)


@app.post("/analyze/stream")
async def analyze_lesion_stream(file: UploadFile = File(...)):
    """Streaming version — sends tokens as they're generated."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    image_bytes = await file.read()
    image_b64   = preprocess_image(image_bytes)

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": "Analyze this skin lesion image.",
                "images": [image_b64]
            }
        ],
        "stream": True,
        "options": {"temperature": 0.1, "num_predict": 512}
    }

    async def token_generator():
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as r:
                async for line in r.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        token = chunk.get("message", {}).get("content", "")
                        if token:
                            yield f"data: {json.dumps({'token': token})}\n\n"
                        if chunk.get("done"):
                            yield "data: [DONE]\n\n"

    return StreamingResponse(token_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn
    import subprocess
    import sys
    import platform
    
    # Auto-kill any existing process on port 8000
    if platform.system() == "Windows":
        try:
            subprocess.run(
                f"netstat -ano | findstr :8000",
                shell=True,
                capture_output=True,
                text=True,
                check=False
            )
            subprocess.run(
                "taskkill /F /IM python.exe /FI 'WINDOWTITLE eq *PathoScan*'",
                shell=True,
                capture_output=True,
                check=False
            )
        except:
            pass
    
    print("=" * 70)
    print("Starting PathoScan API server...")
    print("=" * 70)
    print("Web Interface: http://localhost:8000")
    print("API Docs:     http://localhost:8000/docs")
    print()
    print("IMPORTANT: Make sure Ollama is running!")
    print("  In another terminal, run:")
    print("  $env:OLLAMA_HOST='127.0.0.1:11435' ; ollama serve")
    print("=" * 70)
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
