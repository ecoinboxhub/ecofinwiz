"""
LLM provider implementations with fallback chain.

Priority: Groq (fastest) -> OpenRouter (most capable).
If one fails, automatically falls back to the next.
"""

import json
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

import httpx

from app.config import get_settings
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LLMProvider(ABC):
    @abstractmethod
    async def chat_stream(self, messages: list[dict], model: str = "gpt-4o-mini", temperature: float = 0.7, max_tokens: int = 2048) -> AsyncGenerator[str, None]: ...
    @abstractmethod
    async def chat(self, messages: list[dict], model: str = "gpt-4o-mini", temperature: float = 0.7, max_tokens: int = 2048) -> str: ...


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, base_url: str, api_key: str, default_model: str, extra_headers: Optional[dict] = None, name: str = "unknown"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_model = default_model
        self.extra_headers = extra_headers or {}
        self.name = name

    async def chat_stream(self, messages, model=None, temperature=0.7, max_tokens=2048):
        model = model or self.default_model
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", **self.extra_headers}
        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "stream": True}

        timeout = httpx.Timeout(connect=10.0, read=90.0, write=30.0, pool=30.0)
        limits = httpx.Limits(max_connections=8, max_keepalive_connections=4)
        async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", json=payload, headers=headers) as response:
                if response.status_code != 200:
                    error_body = await response.aread()
                    logger.error(f"[{self.name}] LLM API error {response.status_code}: {error_body[:200]}")
                    yield f"Error: {self.name} returned {response.status_code}"
                    return
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        choices = data.get("choices", [])
                        if choices:
                            content = choices[0].get("delta", {}).get("content", "")
                            if content:
                                yield content
                    except json.JSONDecodeError:
                        continue

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048) -> str:
        model = model or self.default_model
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", **self.extra_headers}
        payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "stream": False}

        async with httpx.AsyncClient(timeout=httpx.Timeout(connect=10.0, read=90.0, write=30.0, pool=30.0), limits=httpx.Limits(max_connections=8, max_keepalive_connections=4)) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(f"[{self.name}] LLM API error {response.status_code}: {response.text[:200]}")
                return ""
            data = response.json()
            choices = data.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "")
            return ""

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(f"{self.base_url}/models", headers={"Authorization": f"Bearer {self.api_key}"})
                return r.status_code == 200
        except Exception:
            return False


class FallbackProvider(LLMProvider):
    """Tries providers in order, falls back to next on failure."""

    def __init__(self, providers: list[OpenAICompatibleProvider]):
        self.providers = providers

    async def chat_stream(self, messages, model=None, temperature=0.7, max_tokens=2048):
        last_error = None
        for provider in self.providers:
            try:
                first_token = True
                async for token in provider.chat_stream(messages, model, temperature, max_tokens):
                    if first_token and token.startswith("Error:"):
                        last_error = token
                        break
                    first_token = False
                    yield token
                else:
                    return
                logger.warning(f"FallbackProvider: {provider.name} failed, trying next...")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"FallbackProvider: {provider.name} exception: {e}, trying next...")
        raise RuntimeError(last_error or "All AI providers failed")

    async def chat(self, messages, model=None, temperature=0.7, max_tokens=2048) -> str:
        for provider in self.providers:
            try:
                result = await provider.chat(messages, model, temperature, max_tokens)
                if result:
                    return result
                logger.warning(f"FallbackProvider: {provider.name} returned empty, trying next...")
            except Exception as e:
                logger.warning(f"FallbackProvider: {provider.name} exception: {e}, trying next...")
        return "I'm sorry, all AI providers are currently unavailable. Please try again later."


def _build_groq_provider() -> Optional[OpenAICompatibleProvider]:
    key = settings.groq_api_key or ""
    if not key:
        return None
    return OpenAICompatibleProvider(
        base_url="https://api.groq.com/openai/v1",
        api_key=key,
        default_model=settings.groq_model or "llama-3.3-70b-versatile",
        name="groq",
    )


def _build_openrouter_provider() -> Optional[OpenAICompatibleProvider]:
    key = settings.openrouter_api_key or ""
    if not key:
        return None
    return OpenAICompatibleProvider(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
        default_model=settings.openrouter_model or "openai/gpt-4o-mini",
        extra_headers={"HTTP-Referer": "https://ecofinwize.app", "X-Title": "EcoFinwize"},
        name="openrouter",
    )


def _build_openai_provider() -> Optional[OpenAICompatibleProvider]:
    key = settings.openai_api_key or ""
    if not key:
        return None
    return OpenAICompatibleProvider(
        base_url="https://api.openai.com/v1",
        api_key=key,
        default_model=settings.openai_model or "gpt-4o-mini",
        name="openai",
    )


def get_provider(name: str = "fallback") -> LLMProvider:
    """Get an LLM provider. Always uses fallback chain for reliability."""
    if name == "groq":
        p = _build_groq_provider()
        if p:
            return p
        logger.warning("Groq not configured, falling back to OpenRouter")
        return _build_openrouter_provider() or _build_groq_provider()

    if name == "openrouter":
        p = _build_openrouter_provider()
        if p:
            return p
        logger.warning("OpenRouter not configured, falling back to Groq")
        return _build_groq_provider() or _build_openrouter_provider()

    # Default: fallback chain (groq -> openrouter -> openai)
    providers = [p for p in [_build_groq_provider(), _build_openrouter_provider(), _build_openai_provider()] if p]
    if not providers:
        raise RuntimeError("No LLM providers configured. Set GROQ_API_KEY, OPENROUTER_API_KEY, or OPENAI_API_KEY.")
    if len(providers) == 1:
        return providers[0]
    return FallbackProvider(providers)
