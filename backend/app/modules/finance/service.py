import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.models import (
    Budget, Transaction, Category, SavingsGoal, SavingsContribution,
)
from app.shared.logger import get_logger

logger = get_logger(__name__)


class FinanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ═══════════════════════════════════════════════════════════
    # BUDGETS
    # ═══════════════════════════════════════════════════════════

    async def list_budgets(self, user_id: uuid.UUID, active_only: bool = False) -> list[Budget]:
        query = select(Budget).where(Budget.user_id == user_id).order_by(Budget.created_at.desc())
        if active_only:
            today = date.today()
            query = query.where(
                and_(
                    Budget.start_date <= today,
                    (Budget.end_date.is_(None) | (Budget.end_date >= today)),
                )
            )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_budget(self, budget_id: uuid.UUID, user_id: uuid.UUID) -> Budget:
        result = await self.db.execute(
            select(Budget).where(Budget.id == budget_id, Budget.user_id == user_id)
        )
        budget = result.scalar_one_or_none()
        if not budget:
            raise NotFoundException("Budget")
        return budget

    async def get_budget_summary(self, user_id: uuid.UUID) -> dict:
        budgets = await self.list_budgets(user_id, active_only=True)
        total_budget = 0.0
        total_spent = 0.0
        over_budget_count = 0
        category_map: dict[str, float] = {}
        for b in budgets:
            spent, _ = await self.get_budget_spending(b.id, user_id)
            limit = float(b.monthly_limit or 0)
            total_budget += limit
            total_spent += spent
            if limit > 0 and spent > limit:
                over_budget_count += 1
            cat = b.category or "Uncategorized"
            category_map[cat] = category_map.get(cat, 0) + spent
        category_breakdown = [{"category": k, "spent": v} for k, v in sorted(category_map.items(), key=lambda x: -x[1])]
        return {
            "total_budget": total_budget,
            "total_spent": total_spent,
            "remaining": total_budget - total_spent,
            "budget_count": len(budgets),
            "over_budget_count": over_budget_count,
            "category_breakdown": category_breakdown,
        }

    async def create_budget(self, user_id: uuid.UUID, data: dict) -> Budget:
        budget = Budget(user_id=user_id, **data)
        if not budget.start_date:
            budget.start_date = date.today()
        self.db.add(budget)
        await self.db.flush()
        return budget

    async def update_budget(self, budget_id: uuid.UUID, user_id: uuid.UUID, data: dict) -> Budget:
        budget = await self.get_budget(budget_id, user_id)
        for key, value in data.items():
            if value is not None:
                setattr(budget, key, value)
        await self.db.flush()
        await self.db.refresh(budget)
        return budget

    async def delete_budget(self, budget_id: uuid.UUID, user_id: uuid.UUID) -> None:
        budget = await self.get_budget(budget_id, user_id)
        await self.db.delete(budget)
        await self.db.flush()

    async def get_budget_spending(self, budget_id: uuid.UUID, user_id: uuid.UUID) -> tuple[float, float]:
        budget = await self.get_budget(budget_id, user_id)
        start = budget.start_date
        end = budget.end_date or date.today()

        result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.budget_id == budget_id,
                Transaction.type == "expense",
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
            )
        )
        spent = float(result.scalar() or 0)
        limit = float(budget.monthly_limit or 0)
        remaining = max(limit - spent, 0)
        return spent, remaining

    # ═══════════════════════════════════════════════════════════
    # ADAPTIVE BUDGET ALGORITHM
    # ═══════════════════════════════════════════════════════════
    """
    Adaptive Budget Algorithm:
    ───────────────────────────
    For users with irregular income (freelancers, SMEs):

    1. Calculate average monthly income over the last N months (default: 3)
    2. For each adaptive budget with percentage_limit set:
       - available = avg_monthly_income * (percentage_limit / 100)
    3. If there's unspent amount from the previous month, roll it over
    4. If the user recorded income this month, use actual income instead of average
       (more responsive to recent changes)

    This replaces fixed monthly_limit with a dynamic value that adjusts
    proportionally to what the user actually earns.
    """

    async def calculate_adaptive_budget(
        self, user_id: uuid.UUID, months_back: int = 3
    ) -> list[dict]:
        today = date.today()
        window_start = today.replace(day=1) - timedelta(days=months_back * 30)
        window_start = window_start.replace(day=1)

        avg_income = await self._get_avg_monthly_income(user_id, window_start, today)

        this_month_income = await self._get_month_income(user_id, today.year, today.month)
        effective_income = this_month_income if this_month_income > 0 else avg_income

        result = await self.db.execute(
            select(Budget).where(
                Budget.user_id == user_id,
                Budget.is_adaptive == True,
                Budget.percentage_limit.isnot(None),
            )
        )
        adaptive_budgets = list(result.scalars().all())

        calculations = []
        for budget in adaptive_budgets:
            pct = float(budget.percentage_limit or 0) / 100
            available = effective_income * pct

            rolled_over = await self._get_previous_rollover(budget.id, user_id, today)

            total_available = available + rolled_over
            spent, _ = await self.get_budget_spending(budget.id, user_id)
            remaining = total_available - spent

            calculations.append({
                "budget_id": budget.id,
                "name": budget.name,
                "category": budget.category,
                "percentage": float(budget.percentage_limit or 0),
                "effective_income": round(effective_income, 2),
                "calculated_limit": round(available, 2),
                "rolled_over": round(rolled_over, 2),
                "total_available": round(total_available, 2),
                "spent": round(spent, 2),
                "remaining": round(max(remaining, 0), 2),
            })

        return calculations

    async def _get_avg_monthly_income(
        self, user_id: uuid.UUID, start: date, end: date
    ) -> float:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "income",
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end,
            )
        )
        total = float(result.scalar() or 0)
        months = max(((end.year - start.year) * 12 + end.month - start.month), 1)
        return total / months

    async def _get_month_income(
        self, user_id: uuid.UUID, year: int, month: int
    ) -> float:
        result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "income",
                and_(
                    func.extract("year", Transaction.transaction_date) == year,
                    func.extract("month", Transaction.transaction_date) == month,
                ),
            )
        )
        return float(result.scalar() or 0)

    async def _get_previous_rollover(
        self, budget_id: uuid.UUID, user_id: uuid.UUID, current_month: date
    ) -> float:
        prev_start = current_month.replace(day=1) - timedelta(days=1)
        prev_start = prev_start.replace(day=1)
        prev_end = current_month.replace(day=1) - timedelta(days=1)

        if prev_start.month == prev_end.month and prev_start.year == prev_end.year:
            result = await self.db.execute(
                select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                    Transaction.budget_id == budget_id,
                    Transaction.type == "expense",
                    Transaction.transaction_date >= prev_start,
                    Transaction.transaction_date <= prev_end,
                )
            )
            spent = float(result.scalar() or 0)

            budget = await self.get_budget(budget_id, user_id)
            pct = float(budget.percentage_limit or 0) / 100
            prev_income = await self._get_month_income(
                user_id, prev_start.year, prev_start.month
            )
            limit = prev_income * pct
            return max(limit - spent, 0)

        return 0.0

    # ═══════════════════════════════════════════════════════════
    # TRANSACTIONS
    # ═══════════════════════════════════════════════════════════

    async def list_transactions(
        self,
        user_id: uuid.UUID,
        type_filter: str | None = None,
        category: str | None = None,
        budget_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Transaction], int]:
        query = select(Transaction).where(Transaction.user_id == user_id)
        count_query = select(func.count(Transaction.id)).where(Transaction.user_id == user_id)

        if type_filter:
            query = query.where(Transaction.type == type_filter)
            count_query = count_query.where(Transaction.type == type_filter)
        if category:
            query = query.where(Transaction.category == category)
            count_query = count_query.where(Transaction.category == category)
        if budget_id:
            query = query.where(Transaction.budget_id == budget_id)
            count_query = count_query.where(Transaction.budget_id == budget_id)
        if start_date:
            query = query.where(Transaction.transaction_date >= start_date)
            count_query = count_query.where(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.where(Transaction.transaction_date <= end_date)
            count_query = count_query.where(Transaction.transaction_date <= end_date)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)

        return list(result.scalars().all()), total

    async def create_transaction(self, user_id: uuid.UUID, data: dict) -> Transaction:
        if not data.get("transaction_date"):
            data["transaction_date"] = date.today()

        if data.get("budget_id"):
            data["budget_id"] = uuid.UUID(data["budget_id"])

        txn = Transaction(user_id=user_id, **data)
        self.db.add(txn)
        await self.db.flush()
        return txn

    async def update_transaction(
        self, txn_id: uuid.UUID, user_id: uuid.UUID, data: dict
    ) -> Transaction:
        result = await self.db.execute(
            select(Transaction).where(Transaction.id == txn_id, Transaction.user_id == user_id)
        )
        txn = result.scalar_one_or_none()
        if not txn:
            raise NotFoundException("Transaction")

        for key, value in data.items():
            if value is not None:
                setattr(txn, key, value)
        await self.db.flush()
        return txn

    async def delete_transaction(self, txn_id: uuid.UUID, user_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(Transaction).where(Transaction.id == txn_id, Transaction.user_id == user_id)
        )
        txn = result.scalar_one_or_none()
        if not txn:
            raise NotFoundException("Transaction")
        await self.db.delete(txn)
        await self.db.flush()

    async def get_spending_summary(
        self, user_id: uuid.UUID, start_date: date, end_date: date | None = None
    ) -> dict:
        if not end_date:
            end_date = date.today()

        income_result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "income",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
        )
        total_income = float(income_result.scalar() or 0)

        expense_result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
        )
        total_expenses = float(expense_result.scalar() or 0)

        cat_result = await self.db.execute(
            select(
                Transaction.category,
                func.coalesce(func.sum(Transaction.amount), 0),
                func.count(Transaction.id),
            ).where(
                Transaction.user_id == user_id,
                Transaction.type == "expense",
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            ).group_by(Transaction.category)
        )
        categories = []
        for row in cat_result.all():
            cat_total = float(row[1])
            pct = (cat_total / total_expenses * 100) if total_expenses > 0 else 0
            categories.append({
                "category": row[0],
                "total": round(cat_total, 2),
                "percentage": round(pct, 1),
                "transaction_count": row[2],
            })

        return {
            "period_start": start_date,
            "period_end": end_date,
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "net": round(total_income - total_expenses, 2),
            "categories": categories,
        }

    # ═══════════════════════════════════════════════════════════
    # CATEGORIES
    # ═══════════════════════════════════════════════════════════

    DEFAULT_CATEGORIES = [
        {"name": "Food & Dining", "icon": "utensils", "type": "expense"},
        {"name": "Transport", "icon": "car", "type": "expense"},
        {"name": "Housing", "icon": "home", "type": "expense"},
        {"name": "Utilities", "icon": "zap", "type": "expense"},
        {"name": "Healthcare", "icon": "heart", "type": "expense"},
        {"name": "Education", "icon": "book", "type": "expense"},
        {"name": "Entertainment", "icon": "music", "type": "expense"},
        {"name": "Shopping", "icon": "shopping-bag", "type": "expense"},
        {"name": "Business Expense", "icon": "briefcase", "type": "expense"},
        {"name": "Salary", "icon": "dollar-sign", "type": "income"},
        {"name": "Freelance", "icon": "laptop", "type": "income"},
        {"name": "Investment", "icon": "trending-up", "type": "income"},
        {"name": "Gift", "icon": "gift", "type": "income"},
        {"name": "Other Income", "icon": "plus-circle", "type": "income"},
        {"name": "Other Expense", "icon": "minus-circle", "type": "expense"},
    ]

    async def list_categories(self, user_id: uuid.UUID, type_filter: str | None = None) -> list[dict]:
        result = await self.db.execute(
            select(Category).where(Category.user_id == user_id)
        )
        user_cats = {c.name: c for c in result.scalars().all()}

        all_categories = []
        for default in self.DEFAULT_CATEGORIES:
            if type_filter and default["type"] != type_filter:
                continue
            all_categories.append(default)

        for user_cat in user_cats.values():
            if type_filter and user_cat.type != type_filter:
                continue
            all_categories.append({
                "id": str(user_cat.id),
                "name": user_cat.name,
                "icon": user_cat.icon,
                "type": user_cat.type,
            })

        seen = set()
        unique = []
        for cat in all_categories:
            key = (cat["name"], cat["type"])
            if key not in seen:
                seen.add(key)
                unique.append(cat)
        return unique

    async def create_category(self, user_id: uuid.UUID, data: dict) -> Category:
        cat = Category(user_id=user_id, **data)
        self.db.add(cat)
        await self.db.flush()
        return cat

    async def delete_category(self, cat_id: uuid.UUID, user_id: uuid.UUID) -> None:
        result = await self.db.execute(
            select(Category).where(Category.id == cat_id, Category.user_id == user_id)
        )
        cat = result.scalar_one_or_none()
        if not cat:
            raise NotFoundException("Category")
        await self.db.delete(cat)
        await self.db.flush()

    # ═══════════════════════════════════════════════════════════
    # SAVINGS GOALS
    # ═══════════════════════════════════════════════════════════

    async def list_savings_goals(
        self, user_id: uuid.UUID, completed_only: bool | None = None
    ) -> list[SavingsGoal]:
        query = select(SavingsGoal).where(SavingsGoal.user_id == user_id)
        if completed_only is True:
            query = query.where(SavingsGoal.is_completed == True)
        elif completed_only is False:
            query = query.where(SavingsGoal.is_completed == False)
        query = query.order_by(SavingsGoal.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_savings_goal(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> SavingsGoal:
        result = await self.db.execute(
            select(SavingsGoal).where(SavingsGoal.id == goal_id, SavingsGoal.user_id == user_id)
        )
        goal = result.scalar_one_or_none()
        if not goal:
            raise NotFoundException("Savings goal")
        return goal

    async def create_savings_goal(self, user_id: uuid.UUID, data: dict) -> SavingsGoal:
        goal = SavingsGoal(user_id=user_id, **data)
        self.db.add(goal)
        await self.db.flush()
        return goal

    async def update_savings_goal(
        self, goal_id: uuid.UUID, user_id: uuid.UUID, data: dict
    ) -> SavingsGoal:
        goal = await self.get_savings_goal(goal_id, user_id)
        for key, value in data.items():
            if value is not None:
                setattr(goal, key, value)
        await self.db.flush()
        await self.db.refresh(goal)
        return goal


    async def delete_savings_goal(self, goal_id: uuid.UUID, user_id: uuid.UUID) -> None:
        goal = await self.get_savings_goal(goal_id, user_id)
        await self.db.delete(goal)
        await self.db.flush()

    async def contribute_to_goal(
        self, goal_id: uuid.UUID, user_id: uuid.UUID, amount: float, note: str | None = None
    ) -> SavingsGoal:
        goal = await self.get_savings_goal(goal_id, user_id)

        contribution = SavingsContribution(goal_id=goal_id, amount=amount, note=note)
        self.db.add(contribution)

        goal.current_amount = float(goal.current_amount or 0) + amount
        if goal.target_amount and goal.current_amount >= float(goal.target_amount):
            goal.current_amount = float(goal.target_amount)
            goal.is_completed = True

        await self.db.flush()
        await self.db.refresh(goal)
        return goal
