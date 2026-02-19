import pytest
import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import Base
from app.core.config import settings
from app.main import app
from httpx import AsyncClient
from app.core.database import get_db

logger = logging.getLogger(__name__)

TEST_DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}_test"

async def create_test_database():
    """Создаёт тестовую БД с автокоммитом."""
    logger.info("Creating test database...")
    root_engine = create_async_engine(
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/postgres",
        isolation_level="AUTOCOMMIT"
    )
    try:
        async with root_engine.connect() as conn:
            logger.info("Terminating connections to test DB...")
            await conn.execute(text(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{settings.DB_NAME}_test'
                AND pid <> pg_backend_pid()
            """))
            logger.info("Dropping test DB if exists...")
            await conn.execute(text(f"DROP DATABASE IF EXISTS {settings.DB_NAME}_test"))
            logger.info("Creating test DB...")
            await conn.execute(text(f"CREATE DATABASE {settings.DB_NAME}_test"))
            logger.info("Test DB created.")
    except Exception as e:
        logger.error(f"Error creating test database: {e}")
        raise
    finally:
        await root_engine.dispose()

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    await create_test_database()
    logger.info("Creating engine for test DB...")
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    logger.info("Dropping and creating tables...")
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()  # Явный коммит DDL
    # Проверим, какие таблицы созданы
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = result.fetchall()
        logger.info(f"Tables in test DB: {tables}")
    logger.info("Tables created.")
    yield engine
    await engine.dispose()

@pytest.fixture(autouse=True)
async def clean_tables(engine):
    """Очищает и создаёт таблицы заново перед каждым тестом."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield

@pytest.fixture
async def db_session(engine):
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        yield session

@pytest.fixture
async def override_get_db(db_session):
    async def _override_get_db():
        yield db_session
    return _override_get_db

@pytest.fixture(autouse=True)
def override_dependencies(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

