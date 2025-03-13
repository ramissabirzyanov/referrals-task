from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Асинхронный генератор, предоставляющий сессию SQLAlchemy для работы с базой данных.

    Используется как зависимость в FastAPI для внедрения сессии в маршруты.
    После завершения работы маршрута сессия автоматически закрывается.
    """
    async with AsyncSessionLocal() as session:
        yield session
