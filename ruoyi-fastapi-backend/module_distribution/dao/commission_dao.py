from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_distribution.entity.do.commission_config_do import CommissionConfig


class CommissionDao:
    @classmethod
    async def get_config_rows(cls, db: AsyncSession, agent_id: int | None) -> Sequence[CommissionConfig]:
        stmt = (
            select(CommissionConfig)
            .where(CommissionConfig.agent_id == agent_id if agent_id is not None else CommissionConfig.agent_id.is_(None))
            .order_by(CommissionConfig.sort_order, CommissionConfig.config_id)
        )
        return (await db.execute(stmt)).scalars().all()

    @classmethod
    async def clear_config_rows(cls, db: AsyncSession, agent_id: int | None) -> None:
        stmt = delete(CommissionConfig).where(
            CommissionConfig.agent_id == agent_id if agent_id is not None else CommissionConfig.agent_id.is_(None)
        )
        await db.execute(stmt)

    @classmethod
    async def add_config_row_dao(cls, db: AsyncSession, payload: dict) -> CommissionConfig:
        entity = CommissionConfig(**payload)
        db.add(entity)
        await db.flush()
        return entity
