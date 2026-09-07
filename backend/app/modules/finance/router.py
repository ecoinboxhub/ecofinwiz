import uuid
from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.modules.auth.dependencies import get_current_user
from app.models import User
from app.modules.finance.schemas import (
    BudgetCreate, BudgetResponse, BudgetSummaryResponse, BudgetUpdate,
    CategoryCreate, CategoryResponse,
    SavingsContributionCreate, SavingsContributionResponse,
    SavingsGoalCreate, SavingsGoalResponse, SavingsGoalUpdate,
    SpendingSummaryResponse,
    TransactionCreate, TransactionResponse, TransactionUpdate,
)
from app.modules.finance.service import FinanceService

router = APIRouter(prefix="/finance", tags=["Finance"])


def get_service(db: AsyncSession = Depends(get_db)) -> FinanceService:
    return FinanceService(db)


# ═══════════════════════════════════════════════════════════════
# BUDGETS
# ═══════════════════════════════════════════════════════════════

@router.get("/budgets", response_model=list[BudgetResponse])
async def list_budgets(
    active_only: bool = Query(False),
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    budgets = await service.list_budgets(current_user.id, active_only=active_only)
    results = []
    for b in budgets:
        spent, remaining = await service.get_budget_spending(b.id, current_user.id)
        resp = BudgetResponse.model_validate(b)
        resp.spent = spent
        resp.remaining = remaining
        results.append(resp)
    return results


@router.get("/budgets/summary", response_model=BudgetSummaryResponse)
async def budget_summary(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    return await service.get_budget_summary(current_user.id)


@router.post("/budgets", response_model=BudgetResponse, status_code=201)
async def create_budget(
    body: BudgetCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    budget = await service.create_budget(current_user.id, body.model_dump(exclude_none=True))
    from app.services.analytics_service import get_analytics
    analytics = get_analytics()
    await analytics.track_budget_created(current_user.id, body.category or "general", body.monthly_limit or 0)
    return BudgetResponse.model_validate(budget)


@router.get("/budgets/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    budget = await service.get_budget(budget_id, current_user.id)
    spent, remaining = await service.get_budget_spending(budget.id, current_user.id)
    resp = BudgetResponse.model_validate(budget)
    resp.spent = spent
    resp.remaining = remaining
    return resp


@router.patch("/budgets/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: uuid.UUID,
    body: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    budget = await service.update_budget(
        budget_id, current_user.id, body.model_dump(exclude_none=True)
    )
    return BudgetResponse.model_validate(budget)


@router.delete("/budgets/{budget_id}", status_code=204)
async def delete_budget(
    budget_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    await service.delete_budget(budget_id, current_user.id)


@router.get("/budgets/adaptive/calculate")
async def calculate_adaptive_budgets(
    months_back: int = Query(3, ge=1, le=12),
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    return await service.calculate_adaptive_budget(current_user.id, months_back=months_back)


# ═══════════════════════════════════════════════════════════════
# TRANSACTIONS
# ═══════════════════════════════════════════════════════════════

@router.get("/transactions")
async def list_transactions(
    type_filter: str | None = Query(None, alias="type"),
    category: str | None = None,
    budget_id: uuid.UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    skip = (page - 1) * per_page
    txns, total = await service.list_transactions(
        current_user.id,
        type_filter=type_filter,
        category=category,
        budget_id=budget_id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=per_page,
    )
    return {
        "items": [TransactionResponse.model_validate(t) for t in txns],
        "total": total,
        "page": page,
        "per_page": per_page,
    }


@router.post("/transactions", response_model=TransactionResponse, status_code=201)
async def create_transaction(
    body: TransactionCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    txn = await service.create_transaction(current_user.id, body.model_dump(exclude_none=True))
    return TransactionResponse.model_validate(txn)


@router.patch("/transactions/{txn_id}", response_model=TransactionResponse)
async def update_transaction(
    txn_id: uuid.UUID,
    body: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    txn = await service.update_transaction(
        txn_id, current_user.id, body.model_dump(exclude_none=True)
    )
    return TransactionResponse.model_validate(txn)


@router.delete("/transactions/{txn_id}", status_code=204)
async def delete_transaction(
    txn_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    await service.delete_transaction(txn_id, current_user.id)


@router.get("/transactions/summary", response_model=SpendingSummaryResponse)
async def spending_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    if not start_date:
        today = date.today()
        start_date = today.replace(day=1)
    return await service.get_spending_summary(current_user.id, start_date, end_date)


# ═══════════════════════════════════════════════════════════════
# CATEGORIES
# ═══════════════════════════════════════════════════════════════

@router.get("/categories")
async def list_categories(
    type_filter: str | None = Query(None, alias="type"),
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    return await service.list_categories(current_user.id, type_filter=type_filter)


@router.post("/categories", response_model=CategoryResponse, status_code=201)
async def create_category(
    body: CategoryCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    cat = await service.create_category(current_user.id, body.model_dump())
    return CategoryResponse.model_validate(cat)


@router.delete("/categories/{cat_id}", status_code=204)
async def delete_category(
    cat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    await service.delete_category(cat_id, current_user.id)


# ═══════════════════════════════════════════════════════════════
# SAVINGS GOALS
# ═══════════════════════════════════════════════════════════════

@router.get("/savings-goals", response_model=list[SavingsGoalResponse])
async def list_savings_goals(
    completed: bool | None = None,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    goals = await service.list_savings_goals(current_user.id, completed_only=completed)
    results = []
    for g in goals:
        resp = SavingsGoalResponse.model_validate(g)
        if g.target_amount and g.target_amount > 0:
            resp.progress = round((float(g.current_amount or 0) / float(g.target_amount)) * 100, 1)
        results.append(resp)
    return results


@router.post("/savings-goals", response_model=SavingsGoalResponse, status_code=201)
async def create_savings_goal(
    body: SavingsGoalCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
    db: AsyncSession = Depends(get_db),
):
    from app.modules.subscriptions.service import SubscriptionService
    svc = SubscriptionService(db)
    if not await svc.check_quota(current_user, "savings_goals_created"):
        raise HTTPException(
            status_code=403,
            detail={
                "code": "QUOTA_EXCEEDED",
                "message": "Free tier allows 1 savings goal. Upgrade to Pro for unlimited goals.",
                "upgrade_plan": svc.get_upgrade_plan(current_user.plan),
            }
        )
    goal = await service.create_savings_goal(current_user.id, body.model_dump(exclude_none=True))
    await svc.increment_usage(current_user.id, "savings_goals_created")

    from app.services.analytics_service import get_analytics
    analytics = get_analytics()
    await analytics.track_savings_goal(current_user.id, body.target_amount or 0)

    return SavingsGoalResponse.model_validate(goal)


@router.get("/savings-goals/{goal_id}", response_model=SavingsGoalResponse)
async def get_savings_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    goal = await service.get_savings_goal(goal_id, current_user.id)
    resp = SavingsGoalResponse.model_validate(goal)
    if goal.target_amount and goal.target_amount > 0:
        resp.progress = round((float(goal.current_amount or 0) / float(goal.target_amount)) * 100, 1)
    return resp


@router.patch("/savings-goals/{goal_id}", response_model=SavingsGoalResponse)
async def update_savings_goal(
    goal_id: uuid.UUID,
    body: SavingsGoalUpdate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    goal = await service.update_savings_goal(
        goal_id, current_user.id, body.model_dump(exclude_none=True)
    )
    resp = SavingsGoalResponse.model_validate(goal)
    if goal.target_amount and goal.target_amount > 0:
        resp.progress = round((float(goal.current_amount or 0) / float(goal.target_amount)) * 100, 1)
    return resp


@router.delete("/savings-goals/{goal_id}", status_code=204)
async def delete_savings_goal(
    goal_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    await service.delete_savings_goal(goal_id, current_user.id)


@router.post("/savings-goals/{goal_id}/contribute", response_model=SavingsGoalResponse)
async def contribute_to_goal(
    goal_id: uuid.UUID,
    body: SavingsContributionCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_service),
):
    goal = await service.contribute_to_goal(
        goal_id, current_user.id, body.amount, note=body.note
    )
    resp = SavingsGoalResponse.model_validate(goal)
    if goal.target_amount and goal.target_amount > 0:
        resp.progress = round((float(goal.current_amount or 0) / float(goal.target_amount)) * 100, 1)
    return resp
