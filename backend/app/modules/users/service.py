from sqlalchemy import select, func, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserBadge, UserPreference, Notification


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_profile(self, user: User) -> User:
        return user

    async def update_profile(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        if kwargs.get("persona_type"):
            user.onboarding_completed = True
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_preferences(self, user: User) -> UserPreference:
        result = await self.db.execute(
            select(UserPreference).where(UserPreference.user_id == user.id)
        )
        prefs = result.scalar_one_or_none()
        if not prefs:
            prefs = UserPreference(user_id=user.id)
            self.db.add(prefs)
            await self.db.flush()
        return prefs

    async def update_preferences(self, user: User, **kwargs) -> UserPreference:
        prefs = await self.get_preferences(user)
        for key, value in kwargs.items():
            if value is not None:
                setattr(prefs, key, value)
        await self.db.flush()
        return prefs

    async def get_progress(self, user: User) -> dict:
        badges_result = await self.db.execute(
            select(UserBadge.badge_key).where(UserBadge.user_id == user.id)
        )
        badges = [row[0] for row in badges_result.all()]

        from app.models import SavingsGoal
        savings_result = await self.db.execute(
            select(func.coalesce(func.sum(SavingsGoal.current_amount), 0)).where(
                SavingsGoal.user_id == user.id
            )
        )
        total_saved = float(savings_result.scalar() or 0)

        active_goals_result = await self.db.execute(
            select(func.count(SavingsGoal.id)).where(
                SavingsGoal.user_id == user.id,
                SavingsGoal.is_completed == False,
            )
        )
        active_goals = active_goals_result.scalar() or 0

        return {
            "lessons_completed": 0,
            "courses_completed": 0,
            "badges": badges,
            "current_streak": 0,
            "total_saved": total_saved,
            "active_goals": active_goals,
        }

    async def get_notifications(self, user: User, skip: int = 0, limit: int = 20) -> list[Notification]:
        result = await self.db.execute(
            select(Notification)
            .where(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def mark_notification_read(self, notification_id: str, user: User) -> Notification | None:
        from uuid import UUID
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == UUID(notification_id),
                Notification.user_id == user.id,
            )
        )
        notification = result.scalar_one_or_none()
        if notification:
            notification.is_read = True
            await self.db.flush()
        return notification

    async def mark_all_notifications_read(self, user: User) -> int:
        from sqlalchemy import update
        result = await self.db.execute(
            update(Notification)
            .where(and_(Notification.user_id == user.id, Notification.is_read == False))
            .values(is_read=True)
        )
        await self.db.flush()
        return result.rowcount
