import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None
    enable_agentic: bool = False


class ChatStreamEvent(BaseModel):
    token: str | None = None
    message_id: str | None = None
    conversation_id: str | None = None
    event: str = "token"  # token, citation, error, done


class FeedbackRequest(BaseModel):
    message_id: str
    rating: int = Field(ge=1, le=5)
    feedback_text: str | None = None


class ConversationSummary(BaseModel):
    id: uuid.UUID
    type: str
    title: str | None = None
    message_count: int = 0
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    rating: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationDetail(BaseModel):
    id: uuid.UUID
    type: str
    title: str | None = None
    is_archived: bool = False
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = []

    model_config = {"from_attributes": True}
