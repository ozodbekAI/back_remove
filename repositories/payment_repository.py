# repositories/payment_repository.py
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Payment

class PaymentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, invoice_id: str, amount: int):
        payment = Payment(user_id=user_id, invoice_id=invoice_id, amount=amount)
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return payment

    async def update_status(self, invoice_id: str, status: str):
        stmt = update(Payment).where(Payment.invoice_id == invoice_id).values(status=status)
        await self.session.execute(stmt)
        await self.session.commit()