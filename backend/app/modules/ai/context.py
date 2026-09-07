"""
Context assembly for AI conversations.

Gathers user profile, financial data, knowledge base context,
and conversation history to provide the LLM with relevant
context for personalized, cited responses.
"""

import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    User, Budget, Transaction, SavingsGoal, AIConversation, AIMessage,
    UserLesson, UserBadge, UserPreference,
)
from app.shared.logger import get_logger

logger = get_logger(__name__)


class ContextAssembler:
    """Assembles user context for AI conversations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def assemble(
        self,
        user: User,
        conversation_type: str,
        conversation_id: uuid.UUID | None = None,
    ) -> str:
        parts = []

        parts.append(await self._user_profile(user))
        parts.append(await self._financial_summary(user))
        parts.append(await self._active_goals(user))
        parts.append(await self._learning_progress(user))

        context = "\n\n".join(parts)

        return context

    async def assemble_with_rag(
        self,
        user: User,
        user_message: str,
        conversation_type: str,
        conversation_id: uuid.UUID | None = None,
    ) -> str:
        parts = []

        parts.append(await self._user_profile(user))
        parts.append(await self._financial_summary(user))
        parts.append(await self._active_goals(user))
        parts.append(await self._learning_progress(user))
        parts.append(await self._rag_context(user_message))

        return "\n\n".join(parts)

    async def _rag_context(self, user_message: str) -> str:
        try:
            from app.modules.intelligence.rag import query_knowledge_base
            results = await query_knowledge_base(user_message, top_k=3)
            if not results:
                return "## Retrieved Knowledge\nNo relevant knowledge base results found."
            lines = ["## Retrieved Knowledge", "The following verified knowledge is available to cite:"]
            for i, r in enumerate(results, 1):
                source = r.get("source", "Knowledge Base")
                text = r.get("text", "")[:300]
                score = r.get("score", 0)
                lines.append(f"[{i}] Source: {source} (relevance: {score:.2f})\n    {text}")
            return "\n".join(lines)
        except ImportError:
            return "## Retrieved Knowledge\nKnowledge base unavailable."
        except Exception as e:
            logger.warning(f"RAG context assembly failed: {e}")
            return "## Retrieved Knowledge\nKnowledge base temporarily unavailable."

    async def _user_profile(self, user: User) -> str:
        persona_label = {
            "freelancer": "Freelancer",
            "sme": "Small Business Owner (SME)",
            "student": "Student",
            "worker": "Public Service Worker / Salary Earner",
        }.get(user.persona_type or "", "General")

        prefs = await self.db.execute(
            select(UserPreference).where(UserPreference.user_id == user.id)
        )
        pref = prefs.scalar_one_or_none()

        return (
            f"## User Profile\n"
            f"- Name: {user.full_name}\n"
            f"- Persona: {persona_label}\n"
            f"- Currency: {pref.currency if pref else 'NGN'}\n"
            f"- Onboarding completed: {'Yes' if user.onboarding_completed else 'No'}\n"
        )

    async def _financial_summary(self, user: User) -> str:
        today = datetime.now(timezone.utc).date()
        month_start = today.replace(day=1)
        last_3_months = month_start - timedelta(days=90)

        income_result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user.id,
                Transaction.type == "income",
                Transaction.transaction_date >= month_start,
            )
        )
        monthly_income = float(income_result.scalar() or 0)

        expense_result = await self.db.execute(
            select(func.coalesce(func.sum(Transaction.amount), 0)).where(
                Transaction.user_id == user.id,
                Transaction.type == "expense",
                Transaction.transaction_date >= month_start,
            )
        )
        monthly_expenses = float(expense_result.scalar() or 0)

        budget_result = await self.db.execute(
            select(Budget).where(
                Budget.user_id == user.id,
                Budget.is_adaptive == True,
            )
        )
        adaptive_count = len(list(budget_result.scalars().all()))

        txn_count_result = await self.db.execute(
            select(func.count(Transaction.id)).where(
                Transaction.user_id == user.id,
                Transaction.transaction_date >= today.replace(day=1),
            )
        )
        txn_count = txn_count_result.scalar() or 0

        return (
            f"## Financial Summary (This Month)\n"
            f"- Month: {month_start.strftime('%B %Y')}\n"
            f"- Income this month: {monthly_income:.2f}\n"
            f"- Expenses this month: {monthly_expenses:.2f}\n"
            f"- Net: {monthly_income - monthly_expenses:.2f}\n"
            f"- Transactions recorded this month: {txn_count}\n"
            f"- Adaptive budgets active: {adaptive_count}\n"
        )

    async def _active_goals(self, user: User) -> str:
        goals_result = await self.db.execute(
            select(SavingsGoal).where(
                SavingsGoal.user_id == user.id,
                SavingsGoal.is_completed == False,
            ).order_by(SavingsGoal.created_at.desc()).limit(5)
        )
        goals = list(goals_result.scalars().all())

        if not goals:
            return "## Savings Goals\nNo active savings goals."

        lines = ["## Savings Goals"]
        for g in goals:
            progress = (float(g.current_amount or 0) / float(g.target_amount) * 100) if g.target_amount > 0 else 0
            due = f", due: {g.target_date}" if g.target_date else ""
            lines.append(f"- {g.name}: {g.current_amount:.0f}/{g.target_amount:.0f} ({progress:.0f}%){due}")

        return "\n".join(lines)

    async def _learning_progress(self, user: User) -> str:
        lessons_result = await self.db.execute(
            select(func.count(UserLesson.id)).where(
                UserLesson.user_id == user.id,
                UserLesson.completed == True,
            )
        )
        completed = lessons_result.scalar() or 0

        badges_result = await self.db.execute(
            select(UserBadge.badge_key).where(UserBadge.user_id == user.id)
        )
        badges = [row[0] for row in badges_result.all()]

        if completed == 0 and not badges:
            return "## Learning Progress\nNo courses started yet."

        badge_str = ", ".join(badges) if badges else "None yet"
        return (
            f"## Learning Progress\n"
            f"- Lessons completed: {completed}\n"
            f"- Badges earned: {badge_str}\n"
        )

    async def get_conversation_history(
        self, conversation_id: uuid.UUID, limit: int = 20
    ) -> list[dict]:
        result = await self.db.execute(
            select(AIMessage)
            .where(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at.asc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role != "system"
        ]
