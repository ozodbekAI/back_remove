# database/models.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    has_free_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    payments = relationship("Payment", back_populates="user")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    invoice_id = Column(String, unique=True, nullable=False, index=True)
    amount = Column(Integer)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payments")