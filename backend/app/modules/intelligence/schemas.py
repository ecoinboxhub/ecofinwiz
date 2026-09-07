from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# --- Documents ---
class DocumentResponse(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    original_filename: str
    content_type: str
    size_bytes: int
    category: str
    tags: Optional[list[str]] = None
    is_indexed: bool
    created_at: datetime
    updated_at: datetime


class DocumentUpdate(BaseModel):
    category: Optional[str] = None
    tags: Optional[list[str]] = None


# --- RAG ---
class RAGQuery(BaseModel):
    query: str
    top_k: int = 5


class RAGResult(BaseModel):
    text: str
    score: float
    source: Optional[str] = None
    document_id: Optional[str] = None


class RAGQueryResponse(BaseModel):
    query: str
    results: list[RAGResult]
    answer: Optional[str] = None


class RAGIndexResponse(BaseModel):
    indexed: int
    total: int


# --- Recommendations ---
class Recommendation(BaseModel):
    content_type: str
    content_id: str
    title: str
    summary: str = ""
    score: float
    reason: str = ""


class RecommendationList(BaseModel):
    items: list[Recommendation]
    based_on: str = ""


# --- Daily Tips ---
class DailyTip(BaseModel):
    id: str
    title: str
    content: str
    category: str
    action_url: Optional[str] = None
