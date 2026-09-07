from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AdCampaignCreate(BaseModel):
    advertiser_name: str
    image_url: str
    target_url: str
    cpm: float
    budget: float = 0
    impressions_bought: int = 0
    target_pages: Optional[list[str]] = None
    is_active: bool = True
    start_date: datetime
    end_date: Optional[datetime] = None


class AdCampaignUpdate(BaseModel):
    advertiser_name: Optional[str] = None
    image_url: Optional[str] = None
    target_url: Optional[str] = None
    cpm: Optional[float] = None
    budget: Optional[float] = None
    impressions_bought: Optional[int] = None
    is_active: Optional[bool] = None
    end_date: Optional[datetime] = None


class AdCampaignResponse(BaseModel):
    id: UUID
    advertiser_name: str
    image_url: str
    target_url: str
    cpm: float
    budget: float
    spent: float
    impressions_bought: int
    impressions_served: int
    target_pages: Optional[list[str]] = None
    is_active: bool
    start_date: datetime
    end_date: Optional[datetime] = None
    created_at: datetime


class AdStatsResponse(BaseModel):
    total_campaigns: int
    active_campaigns: int
    total_impressions: int
    total_revenue: float
    ctr: float
