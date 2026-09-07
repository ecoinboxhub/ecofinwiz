import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


# ── Budget ──
class BudgetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    category: str | None = None
    monthly_limit: float | None = Field(None, gt=0)
    percentage_limit: float | None = Field(None, ge=0, le=100)
    is_adaptive: bool = False
    start_date: date | None = None
    end_date: date | None = None

    @field_validator("category", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        return v if v else None


class BudgetUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = None
    monthly_limit: float | None = Field(None, gt=0)
    percentage_limit: float | None = Field(None, ge=0, le=100)
    is_adaptive: bool | None = None
    start_date: date | None = None
    end_date: date | None = None


class BudgetResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    category: str | None = None
    monthly_limit: float | None = None
    percentage_limit: float | None = None
    is_adaptive: bool = False
    start_date: date
    end_date: date | None = None
    spent: float = 0
    remaining: float = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Transaction ──
class TransactionCreate(BaseModel):
    type: str = Field(pattern="^(income|expense)$")
    amount: float = Field(gt=0)
    category: str = Field(min_length=1, max_length=100)
    description: str | None = None
    transaction_date: date | None = None
    budget_id: str | None = None
    is_recurring: bool = False


class TransactionUpdate(BaseModel):
    type: str | None = Field(None, pattern="^(income|expense)$")
    amount: float | None = Field(None, gt=0)
    category: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    transaction_date: date | None = None
    budget_id: str | None = None
    is_recurring: bool | None = None


class TransactionResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    budget_id: uuid.UUID | None = None
    type: str
    amount: float
    category: str
    description: str | None = None
    transaction_date: date
    is_recurring: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class SpendingSummaryItem(BaseModel):
    category: str
    total: float
    percentage: float
    transaction_count: int


class SpendingSummaryResponse(BaseModel):
    period_start: date
    period_end: date
    total_income: float
    total_expenses: float
    net: float
    categories: list[SpendingSummaryItem]


class BudgetSummaryResponse(BaseModel):
    total_budget: float = 0
    total_spent: float = 0
    remaining: float = 0
    budget_count: int = 0
    over_budget_count: int = 0
    category_breakdown: list[dict] = []


# ── Category ──
class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    icon: str | None = None
    type: str | None = Field(None, pattern="^(income|expense)?$")


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    icon: str | None = None
    type: str | None = None

    model_config = {"from_attributes": True}


# ── Savings Goal ──
class SavingsGoalCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    target_amount: float = Field(gt=0)
    target_date: date | None = None
    category: str | None = None
    icon: str | None = None


class SavingsGoalUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    target_amount: float | None = Field(None, gt=0)
    target_date: date | None = None
    category: str | None = None
    icon: str | None = None


class SavingsGoalResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    target_amount: float
    current_amount: float = 0
    progress: float = 0
    target_date: date | None = None
    category: str | None = None
    icon: str | None = None
    is_completed: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SavingsContributionCreate(BaseModel):
    amount: float = Field(gt=0)
    note: str | None = None


class SavingsContributionResponse(BaseModel):
    id: uuid.UUID
    goal_id: uuid.UUID
    amount: float
    note: str | None = None
    contributed_at: datetime

    model_config = {"from_attributes": True}
