"""
FastAPI application for LinkedIn Post Generator
Multiple API endpoints for different use cases.
"""

import asyncio
import time
from typing import Literal
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables at startup
load_dotenv()

from pipeline import generate_post, generate_variants, stream_post


# ─── Pydantic Models ──────────────────────────────────────────────────────────

ToneType = Literal[
    "professional", "storytelling", "contrarian",
    "inspirational", "educational", "humorous"
]


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=5, max_length=500, description="Topic or idea for the post")
    tone: ToneType = Field(default="professional", description="Writing tone/style")

    model_config = {
        "json_schema_extra": {
            "example": {
                "topic": "Why most developers burn out and how to avoid it",
                "tone": "storytelling",
            }
        }
    }


class VariantsRequest(BaseModel):
    topic: str = Field(..., min_length=5, max_length=500)
    tone: ToneType = Field(default="professional")
    count: int = Field(default=3, ge=1, le=5, description="Number of variants to generate")


class BatchRequest(BaseModel):
    posts: list[GenerateRequest] = Field(..., min_length=1, max_length=10)


class PostResponse(BaseModel):
    topic: str
    tone: str
    post: str
    hashtags: str
    char_count: int
    research: str
    generation_time_seconds: float


class VariantsResponse(BaseModel):
    topic: str
    tone: str
    variants: list[str]
    count: int


class BatchResponse(BaseModel):
    results: list[PostResponse]
    total_generated: int
    total_time_seconds: float


class HealthResponse(BaseModel):
    status: str
    version: str
    endpoints: list[str]


# ─── App Setup ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 LinkedIn Generator API starting up...")
    yield
    print("🛑 LinkedIn Generator API shutting down...")


app = FastAPI(
    title="LinkedIn Post Generator API",
    description="""
    AI-powered LinkedIn post generator using OpenAI Agents SDK.
    
    ## Features
    - **Single post generation** with multi-agent pipeline
    - **Multiple variants** generated in parallel
    - **Batch processing** for multiple topics at once
    - **Streaming** for real-time generation feedback
    - **Hashtag optimization** built-in
    
    ## Agents Pipeline
    `ResearchAgent → ToneAgent → FormatterAgent → HashtagAgent`
    """,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """API health check and endpoint overview."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        endpoints=[
            "POST /generate         — Generate a single LinkedIn post",
            "POST /generate/variants — Generate multiple post variants",
            "POST /generate/batch   — Batch generate posts for multiple topics",
            "GET  /generate/stream  — Stream post generation with progress",
            "GET  /tones            — List available tones",
            "GET  /health           — Health check",
        ],
    )


@app.get("/health", tags=["Health"])
async def health():
    """Simple health check."""
    return {"status": "ok", "timestamp": time.time()}


@app.get("/tones", tags=["Info"])
async def list_tones():
    """List all available tones with descriptions."""
    return {
        "tones": [
            {"name": "professional", "description": "Authoritative, data-driven, executive-level"},
            {"name": "storytelling", "description": "Personal, narrative-first, human and relatable"},
            {"name": "contrarian", "description": "Challenges conventional wisdom, provocative"},
            {"name": "inspirational", "description": "Motivating, forward-looking, empowering"},
            {"name": "educational", "description": "Teacher mode, step-by-step, explains the 'why'"},
            {"name": "humorous", "description": "Wit and levity, unexpected comparisons"},
        ]
    }


@app.post("/generate", response_model=PostResponse, tags=["Generate"])
async def generate_single(request: GenerateRequest):
    """
    Generate a single LinkedIn post.
    
    Runs the full 4-agent pipeline:
    Research → Tone → Format → Hashtags
    """
    start = time.time()
    try:
        result = await generate_post(request.topic, request.tone)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    return PostResponse(
        topic=result.topic,
        tone=result.tone,
        post=result.post,
        hashtags=result.hashtags,
        char_count=result.char_count,
        research=result.research,
        generation_time_seconds=round(time.time() - start, 2),
    )


@app.post("/generate/variants", response_model=VariantsResponse, tags=["Generate"])
async def generate_post_variants(request: VariantsRequest):
    """
    Generate multiple variants of a LinkedIn post in parallel.
    
    Useful for A/B testing different versions of the same topic.
    Max 5 variants per request.
    """
    start = time.time()
    try:
        results = await generate_variants(request.topic, request.tone, request.count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variant generation failed: {str(e)}")

    return VariantsResponse(
        topic=request.topic,
        tone=request.tone,
        variants=[r.post for r in results],
        count=len(results),
    )


@app.post("/generate/batch", response_model=BatchResponse, tags=["Generate"])
async def generate_batch(request: BatchRequest):
    """
    Batch generate posts for multiple topics simultaneously.
    
    All posts are generated in parallel. Max 10 posts per batch.
    """
    start = time.time()
    try:
        tasks = [generate_post(p.topic, p.tone) for p in request.posts]
        results = await asyncio.gather(*tasks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")

    total_time = round(time.time() - start, 2)
    post_responses = [
        PostResponse(
            topic=r.topic,
            tone=r.tone,
            post=r.post,
            hashtags=r.hashtags,
            char_count=r.char_count,
            research=r.research,
            generation_time_seconds=total_time,
        )
        for r in results
    ]

    return BatchResponse(
        results=post_responses,
        total_generated=len(post_responses),
        total_time_seconds=total_time,
    )


@app.get("/generate/stream", tags=["Generate"])
async def generate_stream(
    topic: str = Query(..., min_length=5, description="Topic for the LinkedIn post"),
    tone: ToneType = Query(default="professional", description="Writing tone"),
):
    """
    Stream LinkedIn post generation with real-time progress updates.
    
    Returns a text/event-stream with stage-by-stage updates,
    ending with the final formatted post.
    """

    async def event_generator():
        try:
            async for chunk in stream_post(topic, tone):
                yield f"data: {chunk}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: ERROR: {str(e)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    import os

    uvicorn.run(
        "api.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True,
        log_level="info",
    )