"""
Pinecone RAG (Retrieval-Augmented Generation) service.
Gracefully falls back when Pinecone is not configured.
"""

import asyncio
import hashlib
import json
import logging
from typing import Optional

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_has_pinecone = False
_pinecone_index = None

try:
    from pinecone import Pinecone, ServerlessSpec

    if settings.pinecone_api_key:
        pc = Pinecone(api_key=settings.pinecone_api_key)

        existing = [i["name"] for i in pc.list_indexes()]
        if settings.pinecone_index_name not in existing:
            pc.create_index(
                name=settings.pinecone_index_name,
                dimension=384,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=settings.pinecone_environment),
            )
        _pinecone_index = pc.Index(settings.pinecone_index_name)
        _has_pinecone = True
        logger.info("Pinecone RAG: connected to index %s", settings.pinecone_index_name)
    else:
        logger.info("Pinecone RAG: not configured, running in passthrough mode")
except ImportError:
    logger.info("Pinecone RAG: pinecone client not installed, running in passthrough mode")
except Exception as e:
    logger.warning("Pinecone RAG: failed to initialize: %s", e)


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def _embed_text(text: str) -> list[float]:
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(text).tolist()
    except ImportError:
        pass
    except Exception as e:
        logger.debug("sentence-transformers inference error: %s", e)

    import hashlib
    seed = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
    rng = __import__("random").Random(seed)
    return [rng.random() for _ in range(1536)]


async def _embed_async(text: str) -> list[float]:
    """Prefer the async embedding API; fall back to local (threaded) encode."""
    try:
        from app.services.embedding_service import get_embedding_service

        svc = get_embedding_service()
        if svc:
            vec = await svc.embed(text)
            if vec:
                return vec
    except Exception as e:
        logger.warning("async embedding failed: %s", e)
    return await asyncio.to_thread(_embed_text, text)


async def index_document(
    document_id: str,
    text: str,
    metadata: Optional[dict] = None,
) -> int:
    if not _has_pinecone:
        return 0
    try:
        chunks = _chunk_text(text)
        vectors = []
        for i, chunk in enumerate(chunks):
            vec = await _embed_async(chunk)
            if not vec:
                continue
            chunk_id = f"{document_id}-chunk-{i}"
            meta = {"document_id": document_id, "chunk_index": i, "text": chunk[:1000]}
            if metadata:
                meta.update(metadata)
            vectors.append((chunk_id, vec, meta))
        if vectors:
            await asyncio.to_thread(_pinecone_index.upsert, vectors)
        logger.info("RAG: indexed %d chunks for document %s", len(vectors), document_id)
        return len(vectors)
    except Exception as e:
        logger.error("RAG: index error: %s", e)
        return 0


async def remove_document(document_id: str) -> bool:
    if not _has_pinecone:
        return False
    try:
        await asyncio.to_thread(
            _pinecone_index.delete, filter={"document_id": {"$eq": document_id}}
        )
        return True
    except Exception as e:
        logger.error("RAG: delete error: %s", e)
        return False


async def query_knowledge_base(
    query: str,
    top_k: int = 5,
    filter_dict: Optional[dict] = None,
) -> list[dict]:
    if not _has_pinecone:
        return []

    try:
        query_vec = await _embed_async(query)
        if not query_vec:
            return []
        kwargs: dict = {"vector": query_vec, "top_k": top_k, "include_metadata": True}
        if filter_dict:
            kwargs["filter"] = filter_dict
        results = await asyncio.to_thread(_pinecone_index.query, **kwargs)
        return [
            {
                "text": match["metadata"].get("text", ""),
                "score": match["score"],
                "source": match["metadata"].get("source"),
                "document_id": match["metadata"].get("document_id"),
            }
            for match in results["matches"]
        ]
    except Exception as e:
        logger.error("RAG: query error: %s", e)
        return []


async def answer_with_rag(query: str, top_k: int = 5) -> Optional[dict]:
    results = await query_knowledge_base(query, top_k)
    if not results:
        return None

    context = "\n\n".join([r["text"] for r in results[:3]])

    from app.config import get_settings
    s = get_settings()
    if not s.openrouter_api_key and not s.groq_api_key and not s.openai_api_key:
        return {"query": query, "results": results, "answer": None}

    try:
        from openai import AsyncOpenAI

        if s.openai_api_key:
            client = AsyncOpenAI(api_key=s.openai_api_key)
            model = s.openai_model or "gpt-4o-mini"
        elif s.openrouter_api_key:
            client = AsyncOpenAI(base_url="https://openrouter.ai/api/v1", api_key=s.openrouter_api_key)
            model = s.openrouter_model
        else:
            client = AsyncOpenAI(base_url="https://api.groq.com/openai/v1", api_key=s.groq_api_key)
            model = s.groq_model

        prompt = f"""You are a helpful financial assistant for African youths and SMEs.
Answer the question based on the provided context. If the context doesn't contain enough information, say so.

Context:
{context}

Question: {query}

Answer concisely and practically."""
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1024,
        )
        answer = resp.choices[0].message.content
        return {"query": query, "results": results, "answer": answer}
    except Exception as e:
        logger.error("RAG: answer generation error: %s", e)
        return {"query": query, "results": results, "answer": None}


async def get_index_stats() -> dict:
    if not _has_pinecone:
        return {"status": "not_configured", "vector_count": 0, "index_name": None}
    try:
        stats = _pinecone_index.describe_index_stats()
        return {
            "status": "connected",
            "vector_count": stats.get("total_vector_count", 0),
            "index_name": settings.pinecone_index_name,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
