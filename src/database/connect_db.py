from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase
from src.config import PASSWORD_USER_DB, NAME_DB, NAME_USER

#async
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{NAME_USER}:{PASSWORD_USER_DB}@localhost:5432/{NAME_DB}"

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

async_session_maker = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

#sync

SYNC_DATABASE_URL = f"postgresql+psycopg2://{NAME_USER}:{PASSWORD_USER_DB}@localhost:5432/{NAME_DB}"

async_engine = create_engine(SYNC_DATABASE_URL, echo=True)

session_maker = sessionmaker(bind=async_engine, expire_on_commit=False)
class Base(DeclarativeBase):
    pass