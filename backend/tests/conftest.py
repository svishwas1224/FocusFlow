import sys
import asyncio
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.database import Base, get_session
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def test_engine(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("db") / "test_focusflow.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", future=True, echo=False)

    async def initialize_database():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(initialize_database())
    yield engine
    asyncio.run(engine.dispose())


@pytest.fixture
def async_session_factory(test_engine):
    return sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
def override_get_session(async_session_factory):
    async def _get_test_session():
        async with async_session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = _get_test_session
    yield
    app.dependency_overrides.clear()
