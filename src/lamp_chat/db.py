from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Awaitable, Callable

from sqlalchemy import Executable
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel import MetaData, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from .log import log


@lru_cache
def get_engine(
    db_name: str,
    **kwargs,
) -> AsyncEngine:
    url = f"sqlite+aiosqlite:///{db_name}.db"
    engine = create_async_engine(url, echo=False, **kwargs)
    return engine


class DB:
    def __init__(
        self,
        db_name: str,
        metadata: MetaData,
    ):
        self.db_name = db_name
        self.metadata = metadata
        self.engine = get_engine(db_name)

    async def init(
        self,
        drop_tables: bool = False,
        before_tables_create: Callable[["DB"], Awaitable[None]] | None = None,
        after_tables_create: Callable[["DB"], Awaitable[None]] | None = None,
    ):
        if before_tables_create:
            await before_tables_create(self)

        if drop_tables:
            log.info("Dropping tables...")
            async with self.get_conn() as conn:
                await conn.run_sync(self.metadata.drop_all)

        # Create the tables
        async with self.get_conn() as conn:
            await conn.run_sync(self.metadata.create_all)

        if after_tables_create:
            await after_tables_create(self)

    @asynccontextmanager
    async def get_session(self):
        async with AsyncSession(self.engine) as session:
            yield session

    @asynccontextmanager
    async def get_conn(self):
        async with self.engine.begin() as conn:
            yield conn

    async def exec(self, statement: Executable, **kwargs):
        # async with self.get_async_conn() as conn:
        log.debug(f"Executing statement: {statement}")
        async with self.get_conn() as conn:
            return await conn.execute(statement, **kwargs)


db: DB | None = None


async def get_db(
    db_name: str = "app",
    metadata: MetaData | None = None,
    drop_tables: bool = False,
    before_tables_create: Callable[["DB"], Awaitable[None]] | None = None,
    after_tables_create: Callable[["DB"], Awaitable[None]] | None = None,
) -> DB:
    global db
    if not db:
        log.debug("Creating new DB")
        db = DB(db_name, metadata or SQLModel.metadata)
        await db.init(drop_tables, before_tables_create, after_tables_create)
    return db
