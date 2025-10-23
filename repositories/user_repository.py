from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Payment
from datetime import datetime, timedelta

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, telegram_id: int, username: str = None, first_name: str = None) -> User:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            user = User(telegram_id=telegram_id, username=username, first_name=first_name)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return user

    async def set_free_used(self, telegram_id: int):
        user = await self.get_or_create(telegram_id)
        if not user.has_free_used:
            user.has_free_used = True
            await self.session.commit()
            await self.session.refresh(user)

    async def has_free_used(self, telegram_id: int) -> bool:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user.has_free_used if user else False

    async def has_paid(self, telegram_id: int) -> bool:
        user = await self.get_or_create(telegram_id)
        stmt = select(func.count(Payment.id)).where(and_(Payment.user_id == user.id, Payment.status == 'succeeded'))
        result = await self.session.execute(stmt)
        return result.scalar() > 0

    async def get_stats(self) -> dict:
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        today_start = datetime.combine(today, datetime.min.time())
        yesterday_start = datetime.combine(yesterday, datetime.min.time())

        stmt_today = select(User.id).where(User.created_at >= today_start)
        result_today = await self.session.execute(stmt_today)
        new_today = len(result_today.scalars().all())

        stmt_yesterday = select(User.id).where(
            User.created_at >= yesterday_start, User.created_at < today_start
        )
        result_yesterday = await self.session.execute(stmt_yesterday)
        new_yesterday = len(result_yesterday.scalars().all())

        stmt_total = select(User.id)
        result_total = await self.session.execute(stmt_total)
        total = len(result_total.scalars().all())

        return {"new_today": new_today, "new_yesterday": new_yesterday, "total": total}