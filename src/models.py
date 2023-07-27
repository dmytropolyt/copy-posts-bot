import asyncio
import datetime

from typing import List, Dict, Union

from sqlalchemy import select, String, DateTime, inspect
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


engine = create_async_engine('sqlite+aiosqlite:///groups.db', echo=True)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = 'Group'

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[str] = mapped_column(unique=True)

    def __repr__(self):
        return f'Group id - {self.group_id}'


class GroupDAL:

    def __init__(self, db_session: async_sessionmaker[AsyncSession]):
        self.db_session = db_session

    async def create_group(self, group_id: str) -> None:
        self.db_session.add(Group(group_id=group_id))

        await self.db_session.commit()

    async def select_all_groups(self) -> List[str]:
        groups = await self.db_session.execute(select(Group))

        return [row.Group.group_id for row in groups]


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


asyncio.run(async_main())

async_session = async_sessionmaker(engine, expire_on_commit=False)
