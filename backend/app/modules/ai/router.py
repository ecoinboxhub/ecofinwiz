import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.modules.ai.schemas import (
    ChatRequest, ConversationDetail, ConversationSummary,
    FeedbackRequest, MessageResponse,
)
from app.modules.ai.service import AIService
from app.modules.auth.dependencies import get_current_user
from app.modules.subscriptions.service import SubscriptionService
from app.models import User
from app.services.analytics_service import get_analytics

router = APIRouter(prefix="/ai", tags=["AI"])


def get_service(db: AsyncSession = Depends(get_db)) -> AIService:
    return AIService(db)


def get_groq_service(db: AsyncSession = Depends(get_db)) -> AIService:
    return AIService(db, provider_name="fallback")


async def check_ai_quota(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    svc = SubscriptionService(db)
    if not await svc.check_quota(user, "ai_chats"):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "QUOTA_EXCEEDED",
                "message": "You've used all your AI chats this month. Upgrade to Pro for unlimited chats.",
                "upgrade_plan": svc.get_upgrade_plan(user.plan),
            }
        )
    await svc.increment_usage(user.id, "ai_chats")
    return user


# ══════════════════════════════════════════════════════════════
# STREAMING CHAT (SSE)
# ══════════════════════════════════════════════════════════════

@router.post("/advisor/chat")
async def advisor_chat(
    body: ChatRequest,
    current_user: User = Depends(check_ai_quota),
    service: AIService = Depends(get_service),
    background_tasks: BackgroundTasks = None,
):
    """Chat with the AI Financial Advisor via SSE streaming."""

    async def event_stream():
        async for event_json in service.chat_stream(
            user=current_user,
            message=body.message,
            conversation_type="advisor",
            conversation_id=body.conversation_id,
            enable_agentic=body.enable_agentic,
        ):
            yield f"data: {event_json}\n\n"

    analytics = get_analytics()
    background_tasks.add_task(analytics.track_ai_chat, current_user.id, "kemi", 1)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/advisor/chat/groq")
async def advisor_chat_groq(
    body: ChatRequest,
    current_user: User = Depends(check_ai_quota),
    service: AIService = Depends(get_groq_service),
    background_tasks: BackgroundTasks = None,
):
    """Chat with AI Financial Advisor via Groq (faster, smaller models)."""

    async def event_stream():
        async for event_json in service.chat_stream(
            user=current_user,
            message=body.message,
            conversation_type="advisor",
            conversation_id=body.conversation_id,
            enable_agentic=body.enable_agentic,
        ):
            yield f"data: {event_json}\n\n"

    analytics = get_analytics()
    background_tasks.add_task(analytics.track_ai_chat, current_user.id, "groq", 1)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/mentor/chat")
async def mentor_chat(
    body: ChatRequest,
    current_user: User = Depends(check_ai_quota),
    service: AIService = Depends(get_service),
    background_tasks: BackgroundTasks = None,
):
    """Chat with the AI Business Mentor via SSE streaming."""

    async def event_stream():
        async for event_json in service.chat_stream(
            user=current_user,
            message=body.message,
            conversation_type="mentor",
            conversation_id=body.conversation_id,
            enable_agentic=body.enable_agentic,
        ):
            yield f"data: {event_json}\n\n"

    analytics = get_analytics()
    background_tasks.add_task(analytics.track_ai_chat, current_user.id, "mentor", 1)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ══════════════════════════════════════════════════════════════
# INVESTMENT ADVISOR (MUSA) - STREAMING + SYNC
# ══════════════════════════════════════════════════════════════

@router.post("/investment/chat")
async def investment_chat(
    body: ChatRequest,
    current_user: User = Depends(check_ai_quota),
    service: AIService = Depends(get_service),
):
    """Chat with Musa, the AI Investment Advisor via SSE streaming."""

    async def event_stream():
        try:
            async for event_json in service.chat_stream(
                user=current_user,
                message=body.message,
                conversation_type="investment",
                conversation_id=body.conversation_id,
                enable_agentic=body.enable_agentic,
            ):
                yield f"data: {event_json}\n\n"
        except Exception as e:
            import json as _json
            yield f"data: {_json.dumps({'event': 'error', 'message': 'Service temporarily unavailable. Please try again.'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/investment/chat/sync")
async def investment_chat_sync(
    body: ChatRequest,
    current_user: User = Depends(check_ai_quota),
    service: AIService = Depends(get_service),
):
    """Chat with Musa, the AI Investment Advisor (synchronous)."""

    result = await service.chat(
        user=current_user,
        message=body.message,
        conversation_type="investment",
        conversation_id=body.conversation_id,
        enable_agentic=body.enable_agentic,
    )

    return result


@router.get("/investment/conversations", response_model=list[ConversationSummary])
async def list_investment_conversations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AIService(db)
    skip = (page - 1) * per_page
    conversations, total = await service.list_conversations(
        current_user.id, conv_type="investment", skip=skip, limit=per_page
    )
    return [ConversationSummary.model_validate(c) for c in conversations]


# ══════════════════════════════════════════════════════════════
# FEEDBACK / RATING
# ══════════════════════════════════════════════════════════════

@router.post("/advisor/feedback", status_code=200)
async def submit_feedback(
    body: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AIService(db)
    msg = await service.rate_message(
        message_id=uuid.UUID(body.message_id),
        user_id=current_user.id,
        rating=body.rating,
        feedback_text=body.feedback_text,
    )
    return {"status": "ok", "rating": msg.rating}


@router.post("/advisor/report", status_code=200)
async def report_response(
    body: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AIService(db)
    msg = await service.rate_message(
        message_id=uuid.UUID(body.message_id),
        user_id=current_user.id,
        rating=1,
        feedback_text=f"[REPORTED] {body.feedback_text or 'Inappropriate response'}",
    )
    return {"status": "reported", "message": "Thank you. Our team will review this response."}


# ══════════════════════════════════════════════════════════════
# CONVERSATION MANAGEMENT
# ══════════════════════════════════════════════════════════════

@router.get("/advisor/conversations", response_model=list[ConversationSummary])
async def list_advisor_conversations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AIService(db)
    skip = (page - 1) * per_page
    conversations, total = await service.list_conversations(
        current_user.id, conv_type="advisor", skip=skip, limit=per_page
    )
    return [ConversationSummary.model_validate(c) for c in conversations]


@router.get("/mentor/conversations", response_model=list[ConversationSummary])
async def list_mentor_conversations(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AIService(db)
    skip = (page - 1) * per_page
    conversations, total = await service.list_conversations(
        current_user.id, conv_type="mentor", skip=skip, limit=per_page
    )
    return [ConversationSummary.model_validate(c) for c in conversations]


@router.get("/advisor/conversations/{conv_id}", response_model=ConversationDetail)
async def get_advisor_conversation(
    conv_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AIService(db)
    conv = await service.get_conversation(conv_id, current_user.id)
    messages = await service.get_conversation_messages(conv_id, current_user.id)
    detail = ConversationDetail.model_validate(conv)
    detail.messages = [MessageResponse.model_validate(m) for m in messages]
    return detail


@router.get("/mentor/conversations/{conv_id}", response_model=ConversationDetail)
async def get_mentor_conversation(
    conv_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AIService(db)
    conv = await service.get_conversation(conv_id, current_user.id)
    messages = await service.get_conversation_messages(conv_id, current_user.id)
    detail = ConversationDetail.model_validate(conv)
    detail.messages = [MessageResponse.model_validate(m) for m in messages]
    return detail


@router.patch("/advisor/conversations/{conv_id}/archive", status_code=200)
async def archive_conversation(
    conv_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AIService(db)
    conv = await service.archive_conversation(conv_id, current_user.id)
    return {"status": "archived", "id": str(conv.id)}


@router.delete("/advisor/conversations/{conv_id}", status_code=204)
async def delete_conversation(
    conv_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = AIService(db)
    await service.delete_conversation(conv_id, current_user.id)


# ── Non-streaming fallback ──

@router.post("/advisor/chat/sync")
async def advisor_chat_sync(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Non-streaming chat for clients that don't support SSE. Uses fallback provider chain."""
    service = AIService(db, provider_name="fallback")
    result = await service.chat(
        user=current_user,
        message=body.message,
        conversation_type="advisor",
        conversation_id=body.conversation_id,
        enable_agentic=body.enable_agentic,
    )
    return result


@router.post("/mentor/chat/sync")
async def mentor_chat_sync(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Non-streaming chat for clients that don't support SSE. Uses fallback provider chain."""
    service = AIService(db, provider_name="fallback")
    result = await service.chat(
        user=current_user,
        message=body.message,
        conversation_type="mentor",
        conversation_id=body.conversation_id,
        enable_agentic=body.enable_agentic,
    )
    return result
