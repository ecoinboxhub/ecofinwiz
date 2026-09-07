#!/usr/bin/env python3
"""
Validate API keys against provider health endpoints.

Usage:
    python -m app.scripts.validate_keys

Returns JSON with status for each service and exit code 0 if all required keys valid.
"""

import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from typing import Optional

import httpx


@dataclass
class ValidationResult:
    service: str
    status: str  # valid, invalid, missing, error
    latency_ms: Optional[int] = None
    error: Optional[str] = None


async def validate_openrouter(api_key: str) -> ValidationResult:
    if not api_key:
        return ValidationResult(service="openrouter", status="missing")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://openrouter.ai/api/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return ValidationResult(service="openrouter", status="valid", latency_ms=latency)
            return ValidationResult(
                service="openrouter", status="invalid", latency_ms=latency, error=f"HTTP {resp.status_code}"
            )
    except Exception as e:
        return ValidationResult(service="openrouter", status="error", error=str(e))


async def validate_groq(api_key: str) -> ValidationResult:
    if not api_key:
        return ValidationResult(service="groq", status="missing")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return ValidationResult(service="groq", status="valid", latency_ms=latency)
            return ValidationResult(
                service="groq", status="invalid", latency_ms=latency, error=f"HTTP {resp.status_code}"
            )
    except Exception as e:
        return ValidationResult(service="groq", status="error", error=str(e))


async def validate_pinecone(api_key: str, index_name: str) -> ValidationResult:
    if not api_key or not index_name:
        return ValidationResult(service="pinecone", status="missing")
    start = time.time()
    try:
        # Extract project ID from API key format: pcsk_<project_id>_<rest>
        project_id = api_key.split("_")[1] if "_" in api_key else "unknown"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://controller.{project_id}.pinecone.io/databases",
                headers={"Api-Key": api_key},
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return ValidationResult(service="pinecone", status="valid", latency_ms=latency)
            return ValidationResult(
                service="pinecone", status="invalid", latency_ms=latency, error=f"HTTP {resp.status_code}"
            )
    except Exception as e:
        return ValidationResult(service="pinecone", status="error", error=str(e))


async def validate_paystack(secret_key: str) -> ValidationResult:
    if not secret_key:
        return ValidationResult(service="paystack", status="missing")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.paystack.co/bank",
                headers={"Authorization": f"Bearer {secret_key}"},
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return ValidationResult(service="paystack", status="valid", latency_ms=latency)
            return ValidationResult(
                service="paystack", status="invalid", latency_ms=latency, error=f"HTTP {resp.status_code}"
            )
    except Exception as e:
        return ValidationResult(service="paystack", status="error", error=str(e))


async def validate_flutterwave(secret_key: str) -> ValidationResult:
    if not secret_key:
        return ValidationResult(service="flutterwave", status="missing")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.flutterwave.com/v3/banks/NG",
                headers={"Authorization": f"Bearer {secret_key}"},
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return ValidationResult(service="flutterwave", status="valid", latency_ms=latency)
            return ValidationResult(
                service="flutterwave", status="invalid", latency_ms=latency, error=f"HTTP {resp.status_code}"
            )
    except Exception as e:
        return ValidationResult(service="flutterwave", status="error", error=str(e))


async def validate_sendgrid(api_key: str) -> ValidationResult:
    if not api_key:
        return ValidationResult(service="sendgrid", status="missing")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://api.sendgrid.com/v3/user/profile",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return ValidationResult(service="sendgrid", status="valid", latency_ms=latency)
            return ValidationResult(
                service="sendgrid", status="invalid", latency_ms=latency, error=f"HTTP {resp.status_code}"
            )
    except Exception as e:
        return ValidationResult(service="sendgrid", status="error", error=str(e))


async def validate_posthog(api_key: str, host: str = "https://app.posthog.com") -> ValidationResult:
    if not api_key:
        return ValidationResult(service="posthog", status="missing")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{host}/api/projects/",
                headers={"Authorization": f"Bearer {api_key}"},
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return ValidationResult(service="posthog", status="valid", latency_ms=latency)
            return ValidationResult(
                service="posthog", status="invalid", latency_ms=latency, error=f"HTTP {resp.status_code}"
            )
    except Exception as e:
        return ValidationResult(service="posthog", status="error", error=str(e))


async def validate_newsapi(api_key: str) -> ValidationResult:
    if not api_key:
        return ValidationResult(service="newsapi", status="missing")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://newsapi.org/v2/top-headlines",
                params={"country": "us", "pageSize": 1, "apiKey": api_key},
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return ValidationResult(service="newsapi", status="valid", latency_ms=latency)
            return ValidationResult(
                service="newsapi", status="invalid", latency_ms=latency, error=f"HTTP {resp.status_code}"
            )
    except Exception as e:
        return ValidationResult(service="newsapi", status="error", error=str(e))


async def validate_exchange_rate(api_key: str) -> ValidationResult:
    if not api_key:
        return ValidationResult(service="exchangerate", status="missing")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD",
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return ValidationResult(service="exchangerate", status="valid", latency_ms=latency)
            return ValidationResult(
                service="exchangerate", status="invalid", latency_ms=latency, error=f"HTTP {resp.status_code}"
            )
    except Exception as e:
        return ValidationResult(service="exchangerate", status="error", error=str(e))


async def validate_jina(api_key: str) -> ValidationResult:
    if not api_key:
        return ValidationResult(service="jina", status="missing")
    start = time.time()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.jina.ai/v1/embeddings",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"input": ["test"], "model": "jina-embeddings-v3"},
            )
            latency = int((time.time() - start) * 1000)
            if resp.status_code == 200:
                return ValidationResult(service="jina", status="valid", latency_ms=latency)
            return ValidationResult(
                service="jina", status="invalid", latency_ms=latency, error=f"HTTP {resp.status_code}"
            )
    except Exception as e:
        return ValidationResult(service="jina", status="error", error=str(e))


async def main():
    from app.config import get_settings

    settings = get_settings()

    results = []

    # Required in production
    results.append(await validate_openrouter(settings.openrouter_api_key))
    results.append(await validate_groq(settings.groq_api_key))
    results.append(await validate_pinecone(settings.pinecone_api_key, settings.pinecone_index_name))
    results.append(await validate_paystack(settings.paystack_secret_key))

    # Optional
    results.append(await validate_flutterwave(settings.flutterwave_secret_key))
    results.append(await validate_sendgrid(settings.sendgrid_api_key))
    results.append(await validate_posthog(settings.posthog_api_key, settings.posthog_host))
    results.append(await validate_newsapi(settings.newsapi_key))
    results.append(await validate_exchange_rate(settings.exchange_rate_api_key))
    results.append(await validate_jina(settings.jina_embedding_api_key))

    # Output JSON
    output = [asdict(r) for r in results]
    print(json.dumps(output, indent=2))

    # Exit code: 0 if all required services valid or missing (not invalid/error)
    required_services = {"openrouter", "groq", "pinecone", "paystack"}
    has_required_llm = any(r.status == "valid" for r in results if r.service in ("openrouter", "groq"))

    failed = []
    for r in results:
        if r.service in required_services:
            if r.service in ("openrouter", "groq"):
                if not has_required_llm and r.status in ("invalid", "error"):
                    failed.append(r.service)
            elif r.status in ("invalid", "error"):
                failed.append(r.service)

    if failed:
        print(f"Required services failed: {failed}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())