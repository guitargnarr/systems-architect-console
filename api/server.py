"""
Systems Architect Console - Backend API
Queries multiple Ollama models in parallel for holistic analysis
"""

import asyncio
import json
import subprocess
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
import threading

app = FastAPI(
    title="Systems Architect Console API",
    description="Multi-model query API for holistic analysis",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define all 19 models with their domains and descriptions
MODELS = {
    "unified-systems-architect": {
        "domain": "meta",
        "color": "#f97316",
        "description": "Meta-expert synthesizing all domains",
        "priority": 1
    },
    "llm-orchestration-ontology": {
        "domain": "technical",
        "color": "#3b82f6",
        "description": "LLM orchestration patterns, multi-agent systems"
    },
    "prompt-engineering-expert": {
        "domain": "technical",
        "color": "#3b82f6",
        "description": "Prompting techniques, debugging, optimization"
    },
    "kg-traversal-expert": {
        "domain": "technical",
        "color": "#3b82f6",
        "description": "Knowledge graph algorithms, SPARQL, Cypher"
    },
    "app-architecture-expert": {
        "domain": "technical",
        "color": "#3b82f6",
        "description": "Web architecture patterns, SSR, SPA, microservices"
    },
    "performance-percentiles-expert": {
        "domain": "technical",
        "color": "#3b82f6",
        "description": "p50/p95/p99 metrics, SLOs, error budgets"
    },
    "wealth-mindset": {
        "domain": "wealth",
        "color": "#22c55e",
        "description": "Wealth thinking, leverage, ownership mindset"
    },
    "passive-income-expert": {
        "domain": "wealth",
        "color": "#22c55e",
        "description": "Passive income streams, investment strategies"
    },
    "real-estate-investor": {
        "domain": "wealth",
        "color": "#22c55e",
        "description": "Real estate strategies, BRRRR, financing"
    },
    "deal-structuring-expert": {
        "domain": "wealth",
        "color": "#22c55e",
        "description": "M&A, acquisitions, deal financing"
    },
    "business-tax-2026": {
        "domain": "tax",
        "color": "#a855f7",
        "description": "2026 tax laws, OBBBA provisions, compliance"
    },
    "cpa-wealth-advisor": {
        "domain": "tax",
        "color": "#a855f7",
        "description": "Business owner tax optimization, retirement"
    },
    "homeowner-tax-strategies": {
        "domain": "tax",
        "color": "#a855f7",
        "description": "Homeowner deductions, 1031 exchanges, depreciation"
    },
    "ngo-corporate-structures": {
        "domain": "tax",
        "color": "#a855f7",
        "description": "Nonprofit structures, 501c3/c4, beneficial ownership"
    },
    "skill-stack-expert": {
        "domain": "personal",
        "color": "#ec4899",
        "description": "8 power skill stacks for career acceleration"
    },
    "skill-stacker": {
        "domain": "personal",
        "color": "#ec4899",
        "description": "Skill development strategy, rare combinations"
    },
    "productivity-systems-expert": {
        "domain": "personal",
        "color": "#ec4899",
        "description": "Time management, focus systems, GTD"
    },
    "world-model-expert": {
        "domain": "personal",
        "color": "#ec4899",
        "description": "Mental models, systems thinking, Bayesian reasoning"
    },
    "english-to-spanish": {
        "domain": "utility",
        "color": "#64748b",
        "description": "English to Spanish translation"
    }
}

DOMAIN_COLORS = {
    "meta": {"bg": "#f97316", "label": "Meta"},
    "technical": {"bg": "#3b82f6", "label": "Technical"},
    "wealth": {"bg": "#22c55e", "label": "Wealth"},
    "tax": {"bg": "#a855f7", "label": "Tax/Legal"},
    "personal": {"bg": "#ec4899", "label": "Personal"},
    "utility": {"bg": "#64748b", "label": "Utility"}
}


class QueryRequest(BaseModel):
    prompt: str
    models: Optional[list[str]] = None  # None means query all
    timeout: Optional[int] = 120


class ModelResponse(BaseModel):
    model: str
    domain: str
    color: str
    description: str
    response: Optional[str] = None
    error: Optional[str] = None
    duration_ms: int
    status: str  # "success", "error", "timeout"


class QueryResponse(BaseModel):
    prompt: str
    total_duration_ms: int
    models_queried: int
    models_succeeded: int
    responses: list[ModelResponse]


def query_ollama_model(model_name: str, prompt: str, timeout: int = 120) -> dict:
    """Query a single Ollama model synchronously"""
    start_time = time.time()
    model_info = MODELS.get(model_name, {})

    try:
        result = subprocess.run(
            ["ollama", "run", model_name],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        duration_ms = int((time.time() - start_time) * 1000)

        if result.returncode == 0:
            return {
                "model": model_name,
                "domain": model_info.get("domain", "unknown"),
                "color": model_info.get("color", "#64748b"),
                "description": model_info.get("description", ""),
                "response": result.stdout.strip(),
                "error": None,
                "duration_ms": duration_ms,
                "status": "success"
            }
        else:
            return {
                "model": model_name,
                "domain": model_info.get("domain", "unknown"),
                "color": model_info.get("color", "#64748b"),
                "description": model_info.get("description", ""),
                "response": None,
                "error": result.stderr.strip() or "Unknown error",
                "duration_ms": duration_ms,
                "status": "error"
            }

    except subprocess.TimeoutExpired:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "model": model_name,
            "domain": model_info.get("domain", "unknown"),
            "color": model_info.get("color", "#64748b"),
            "description": model_info.get("description", ""),
            "response": None,
            "error": f"Timeout after {timeout} seconds",
            "duration_ms": duration_ms,
            "status": "timeout"
        }
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "model": model_name,
            "domain": model_info.get("domain", "unknown"),
            "color": model_info.get("color", "#64748b"),
            "description": model_info.get("description", ""),
            "response": None,
            "error": str(e),
            "duration_ms": duration_ms,
            "status": "error"
        }


@app.get("/")
async def root():
    return {
        "service": "Systems Architect Console API",
        "version": "1.0.0",
        "models_available": len(MODELS),
        "endpoints": {
            "/models": "List all available models",
            "/domains": "List domain categories",
            "/query": "POST - Query models with a prompt",
            "/query/{model}": "POST - Query a single model"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "models_configured": len(MODELS)}


@app.get("/models")
async def list_models():
    """List all available models with their metadata"""
    return {
        "total": len(MODELS),
        "models": [
            {
                "name": name,
                **info
            }
            for name, info in MODELS.items()
        ]
    }


@app.get("/domains")
async def list_domains():
    """List all domain categories"""
    return DOMAIN_COLORS


@app.post("/query", response_model=QueryResponse)
async def query_models(request: QueryRequest):
    """
    Query multiple Ollama models in parallel.
    If models list is empty/None, queries all models.
    """
    start_time = time.time()

    # Determine which models to query
    models_to_query = request.models if request.models else list(MODELS.keys())

    # Validate model names
    invalid_models = [m for m in models_to_query if m not in MODELS]
    if invalid_models:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid model names: {invalid_models}"
        )

    # Query models in parallel using ThreadPoolExecutor
    responses = []
    with ThreadPoolExecutor(max_workers=min(len(models_to_query), 8)) as executor:
        futures = {
            executor.submit(query_ollama_model, model, request.prompt, request.timeout): model
            for model in models_to_query
        }

        for future in futures:
            try:
                result = future.result()
                responses.append(result)
            except Exception as e:
                model_name = futures[future]
                model_info = MODELS.get(model_name, {})
                responses.append({
                    "model": model_name,
                    "domain": model_info.get("domain", "unknown"),
                    "color": model_info.get("color", "#64748b"),
                    "description": model_info.get("description", ""),
                    "response": None,
                    "error": str(e),
                    "duration_ms": 0,
                    "status": "error"
                })

    # Sort responses: meta first, then by domain, then alphabetically
    domain_order = {"meta": 0, "technical": 1, "wealth": 2, "tax": 3, "personal": 4, "utility": 5}
    responses.sort(key=lambda r: (domain_order.get(r["domain"], 99), r["model"]))

    total_duration_ms = int((time.time() - start_time) * 1000)
    models_succeeded = sum(1 for r in responses if r["status"] == "success")

    return QueryResponse(
        prompt=request.prompt,
        total_duration_ms=total_duration_ms,
        models_queried=len(models_to_query),
        models_succeeded=models_succeeded,
        responses=[ModelResponse(**r) for r in responses]
    )


@app.post("/query/{model_name}")
async def query_single_model(model_name: str, request: QueryRequest):
    """Query a single Ollama model"""
    if model_name not in MODELS:
        raise HTTPException(
            status_code=404,
            detail=f"Model '{model_name}' not found. Available: {list(MODELS.keys())}"
        )

    result = query_ollama_model(model_name, request.prompt, request.timeout)
    return ModelResponse(**result)


@app.get("/query/domains/{domain}")
async def get_models_by_domain(domain: str):
    """Get all models for a specific domain"""
    if domain not in DOMAIN_COLORS:
        raise HTTPException(
            status_code=404,
            detail=f"Domain '{domain}' not found. Available: {list(DOMAIN_COLORS.keys())}"
        )

    models = [
        {"name": name, **info}
        for name, info in MODELS.items()
        if info.get("domain") == domain
    ]

    return {
        "domain": domain,
        "label": DOMAIN_COLORS[domain]["label"],
        "color": DOMAIN_COLORS[domain]["bg"],
        "models": models
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765)
