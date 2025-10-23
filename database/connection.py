# database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import settings
from utils.logger import logger

engine = create_async_engine(settings.database_url.replace("postgresql://", "postgresql+asyncpg://"), echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        from .models import Base
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")