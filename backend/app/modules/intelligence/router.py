import os
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.modules.auth.dependencies import get_current_user
from app.models import User
from app.modules.intelligence import service
from app.modules.intelligence.schemas import (
    DocumentResponse, DocumentUpdate,
    RAGQuery, RAGQueryResponse,
    RecommendationList, DailyTip,
)

router = APIRouter()


# =====================================================================
# DOCUMENTS
# =====================================================================

@router.post("/documents/upload", status_code=201, tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...),
    category: str = Form("general"),
    tags: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else None
    doc = await service.upload_document(file, user.id, category, tag_list, db)
    return DocumentResponse(
        id=doc.id, user_id=doc.user_id, filename=doc.filename,
        original_filename=doc.original_filename, content_type=doc.content_type,
        size_bytes=doc.size_bytes, category=doc.category,
        tags=doc.tags.get("tags") if doc.tags else None,
        is_indexed=doc.is_indexed, created_at=doc.created_at, updated_at=doc.updated_at,
    )


@router.get("/documents", tags=["Documents"])
async def list_documents(
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    docs = await service.list_documents(user.id, db, category)
    return [DocumentResponse(
        id=d.id, user_id=d.user_id, filename=d.filename,
        original_filename=d.original_filename, content_type=d.content_type,
        size_bytes=d.size_bytes, category=d.category,
        tags=d.tags.get("tags") if d.tags else None,
        is_indexed=d.is_indexed, created_at=d.created_at, updated_at=d.updated_at,
    ) for d in docs]


@router.get("/documents/{doc_id}", tags=["Documents"])
async def get_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doc = await service.get_document(doc_id, user.id, db)
    return DocumentResponse(
        id=doc.id, user_id=doc.user_id, filename=doc.filename,
        original_filename=doc.original_filename, content_type=doc.content_type,
        size_bytes=doc.size_bytes, category=doc.category,
        tags=doc.tags.get("tags") if doc.tags else None,
        is_indexed=doc.is_indexed, created_at=doc.created_at, updated_at=doc.updated_at,
    )


@router.get("/documents/{doc_id}/download", tags=["Documents"])
async def download_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    filepath, filename, content_type = await service.get_document_file(doc_id, user.id, db)
    return FileResponse(filepath, media_type=content_type, filename=filename)


@router.patch("/documents/{doc_id}", tags=["Documents"])
async def update_document(
    doc_id: UUID,
    data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    doc = await service.update_document(doc_id, data, user.id, db)
    return DocumentResponse(
        id=doc.id, user_id=doc.user_id, filename=doc.filename,
        original_filename=doc.original_filename, content_type=doc.content_type,
        size_bytes=doc.size_bytes, category=doc.category,
        tags=doc.tags.get("tags") if doc.tags else None,
        is_indexed=doc.is_indexed, created_at=doc.created_at, updated_at=doc.updated_at,
    )


@router.delete("/documents/{doc_id}", status_code=204, tags=["Documents"])
async def delete_document(
    doc_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    await service.delete_document(doc_id, user.id, db)


# =====================================================================
# RAG — Knowledge Base
# =====================================================================

@router.post("/rag/query", tags=["RAG"])
async def query_rag(
    data: RAGQuery,
    user: User = Depends(get_current_user),
):
    return await service.query_rag(data)


@router.get("/rag/status", tags=["RAG"])
async def rag_status(
    user: User = Depends(get_current_user),
):
    return await service.get_rag_status()


# =====================================================================
# RECOMMENDATIONS
# =====================================================================

@router.get("/recommendations", tags=["Recommendations"])
async def get_recommendations(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await service.get_recommendations(user.id, db)


# =====================================================================
# DAILY TIPS
# =====================================================================

@router.get("/tips/daily", tags=["Tips"])
async def get_daily_tip(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await service.get_daily_tip(user, db)


@router.get("/tips", tags=["Tips"])
async def get_tips_by_category(
    category: str = Query("savings"),
    limit: int = Query(5, ge=1, le=20),
    user: User = Depends(get_current_user),
):
    return await service.get_tips_by_category(category, limit)
