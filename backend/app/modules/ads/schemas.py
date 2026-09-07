from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AdResponse(BaseModel):
    id: str
    image_url: str
    target_url: str
    sponsor_name: str
    label: str


class ImpressionRequest(BaseModel):
    campaign_id: UUID


class ImpressionResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    amount_earned: float
    served_at: datetime
