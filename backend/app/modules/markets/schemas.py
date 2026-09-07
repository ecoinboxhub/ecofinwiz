from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class MarketIndex(BaseModel):
    symbol: str
    name: str
    country: str
    region: str = Field(description="africa | global")
    currency: str
    value: float
    change: float = Field(description="absolute change from previous close")
    change_pct: float = Field(description="percentage change from previous close")
    status: str = Field(default="closed", description="open | closed")


class CryptoTicker(BaseModel):
    symbol: str
    name: str
    currency: str = "USD"
    value: float
    change: float
    change_pct: float


class CommodityPrice(BaseModel):
    symbol: str
    name: str
    unit: str
    currency: str = "USD"
    value: float
    change: float
    change_pct: float


class RegionIndices(BaseModel):
    region: str
    name: str
    indices: list[MarketIndex]


class MarketsOverview(BaseModel):
    as_of: datetime
    disclaimer: str
    regions: list[RegionIndices]
    crypto: list[CryptoTicker]
    commodities: list[CommodityPrice]


def _now() -> datetime:
    return datetime.now(timezone.utc)