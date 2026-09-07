from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# --- Business Plans ---
class BusinessPlanGenerate(BaseModel):
    business_name: str
    industry: str
    description: str
    target_market: str = ""
    revenue_model: str = ""
    funding_needed: Optional[float] = None
    team_size: Optional[int] = None


class BusinessPlanResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: dict
    status: str
    created_at: datetime
    updated_at: datetime


# --- Tasks ---
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None


class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# --- Invoices ---
class InvoiceItem(BaseModel):
    description: str
    quantity: float = 1
    unit_price: float = 0
    amount: float = 0


class InvoiceCreate(BaseModel):
    client_name: str
    client_email: Optional[str] = None
    client_address: Optional[str] = None
    items: list[InvoiceItem] = []
    tax_rate: float = 0
    currency: str = "NGN"
    notes: Optional[str] = None
    due_date: Optional[datetime] = None


class InvoiceUpdate(BaseModel):
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_address: Optional[str] = None
    items: Optional[list[InvoiceItem]] = None
    tax_rate: Optional[float] = None
    currency: Optional[str] = None
    notes: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: UUID
    user_id: UUID
    number: str
    client_name: str
    client_email: Optional[str] = None
    client_address: Optional[str] = None
    items: list[dict]
    subtotal: float
    tax_rate: float
    tax_amount: float
    total: float
    currency: str
    status: str
    notes: Optional[str] = None
    due_date: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
