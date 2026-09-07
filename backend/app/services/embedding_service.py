"""
External embedding API service for RAG vector generation.

Alternative to local sentence-transformers inference.
Supports OpenAI Embeddings and Jina AI Embeddings v2.
"""

from typing import Optional

import httpx

from app.config import get_settings
from app.shared.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class OpenAIEmbeddingService:
    """OpenAI text-embedding-3-small via API."""

    def __init__(self):
        self.api_key = settings.openai_api_key or settings.openrouter_api_key
        self.model = "text-embedding-3-small"
        self.dimensions = 384

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def embed(self, text: str) -> Optional[list[float]]:
        if not self.is_configured:
            return None
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={"input": text, "model": self.model, "dimensions": self.dimensions},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["data"][0]["embedding"]
                logger.warning("OpenAI Embedding error %d: %s", resp.status_code, resp.text[:100])
                return None
        except Exception as e:
            logger.debug("OpenAI Embedding error: %s", e)
            return None

    async def embed_batch(self, texts: list[str]) -> list[Optional[list[float]]]:
        if not self.is_configured:
            return [None] * len(texts)
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={"input": texts, "model": self.model, "dimensions": self.dimensions},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    result = [None] * len(texts)
                    for emb in data["data"]:
                        result[emb["index"]] = emb["embedding"]
                    return result
                return [None] * len(texts)
        except Exception as e:
            logger.debug("OpenAI Embedding batch error: %s", e)
            return [None] * len(texts)


class JinaEmbeddingService:
    """Jina AI Embeddings v2 (open-source alternative)."""

    def __init__(self):
        self.api_key = settings.jina_embedding_api_key
        self.base_url = "https://api.jina.ai/v1/embeddings"
        self.model = "jina-embeddings-v2-base-en"

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def embed(self, text: str) -> Optional[list[float]]:
        if not self.is_configured:
            return None
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    self.base_url,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={"input": [text], "model": self.model},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["data"][0]["embedding"]
                return None
        except Exception as e:
            logger.debug("Jina Embedding error: %s", e)
            return None


def get_embedding_service():
    """Returns the best available embedding service."""
    openai = OpenAIEmbeddingService()
    if openai.is_configured:
        logger.info("Embeddings: using OpenAI (%s)", openai.model)
        return openai

    jina = JinaEmbeddingService()
    if jina.is_configured:
        logger.info("Embeddings: using Jina AI (%s)", jina.model)
        return jina

    logger.info("Embeddings: no external service configured, using local sentence-transformers")
    return None
