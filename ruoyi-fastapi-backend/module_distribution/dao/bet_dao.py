from collections.abc import Sequence

from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_distribution.entity.do.agent_info_do import AgentInfo
from module_distribution.entity.do.bet_link_do import BetLink
from module_distribution.entity.do.bet_record_do import BetRecord
from module_distribution.entity.do.commission_config_do import CommissionConfig
from module_distribution.entity.do.earnings_do import AgentEarnings, UserEarnings


class BetDao:
    """
    投注域数据库操作层
    """

    @classmethod
    async def add_bet_link_dao(cls, db: AsyncSession, payload: dict) -> BetLink:
        entity = BetLink(**payload)
        db.add(entity)
        await db.flush()
        return entity

    @classmethod
    async def get_bet_link_by_id(cls, db: AsyncSession, link_id: int) -> BetLink | None:
        return (await db.execute(select(BetLink).where(BetLink.link_id == link_id))).scalars().first()

    @classmethod
    async def get_bet_link_by_token(cls, db: AsyncSession, token: str) -> BetLink | None:
        return (await db.execute(select(BetLink).where(BetLink.link_token == token))).scalars().first()

    @classmethod
    async def get_bet_link_list_by_agent(
        cls, db: AsyncSession, agent_id: int, link_name: str | None, status: int | None
    ) -> Sequence[BetLink]:
        stmt = (
            select(BetLink)
            .where(
                BetLink.agent_id == agent_id,
                BetLink.link_name.like(f'%{link_name}%') if link_name else True,
                BetLink.status == status if status is not None else True,
            )
            .order_by(desc(BetLink.link_id))
        )
        return (await db.execute(stmt)).scalars().all()

    @classmethod
    async def update_bet_link_dao(cls, db: AsyncSession, link_id: int, **values) -> None:
        await db.execute(update(BetLink).where(BetLink.link_id == link_id).values(**values))

    @classmethod
    async def count_confirmed_records_by_link(cls, db: AsyncSession, link_id: int) -> int:
        stmt = (
            select(func.count('*'))
            .select_from(BetRecord)
            .where(BetRecord.link_id == link_id, BetRecord.is_confirmed == 1)
        )
        return (await db.execute(stmt)).scalar() or 0

    @classmethod
    async def get_bet_record_by_link_and_user(cls, db: AsyncSession, link_id: int, user_id: int) -> BetRecord | None:
        stmt = select(BetRecord).where(BetRecord.link_id == link_id, BetRecord.user_id == user_id)
        return (await db.execute(stmt)).scalars().first()

    @classmethod
    async def add_bet_record_dao(cls, db: AsyncSession, payload: dict) -> BetRecord:
        entity = BetRecord(**payload)
        db.add(entity)
        await db.flush()
        return entity

    @classmethod
    async def update_bet_record_dao(cls, db: AsyncSession, record_id: int, **values) -> None:
        await db.execute(update(BetRecord).where(BetRecord.record_id == record_id).values(**values))

    @classmethod
    async def get_confirmed_records_by_link(cls, db: AsyncSession, link_id: int) -> Sequence[BetRecord]:
        stmt = (
            select(BetRecord)
            .where(BetRecord.link_id == link_id, BetRecord.is_confirmed == 1)
            .order_by(BetRecord.record_id)
        )
        return (await db.execute(stmt)).scalars().all()

    @classmethod
    async def get_my_bet_records(cls, db: AsyncSession, user_id: int) -> Sequence[tuple[BetRecord, BetLink]]:
        stmt = (
            select(BetRecord, BetLink)
            .join(BetLink, BetRecord.link_id == BetLink.link_id)
            .where(BetRecord.user_id == user_id)
            .order_by(desc(BetRecord.record_id))
        )
        return (await db.execute(stmt)).all()

    @classmethod
    async def add_user_earning_dao(cls, db: AsyncSession, payload: dict) -> UserEarnings:
        entity = UserEarnings(**payload)
        db.add(entity)
        await db.flush()
        return entity

    @classmethod
    async def add_agent_earning_dao(cls, db: AsyncSession, payload: dict) -> AgentEarnings:
        entity = AgentEarnings(**payload)
        db.add(entity)
        await db.flush()
        return entity

    @classmethod
    async def get_agent_info_by_id(cls, db: AsyncSession, agent_id: int) -> AgentInfo | None:
        return (await db.execute(select(AgentInfo).where(AgentInfo.agent_id == agent_id))).scalars().first()

    @classmethod
    async def get_commission_config_for_agent(
        cls, db: AsyncSession, agent_id: int, profit: float
    ) -> CommissionConfig | None:
        stmt = (
            select(CommissionConfig)
            .where(
                CommissionConfig.agent_id == agent_id,
                CommissionConfig.profit_min <= profit,
                CommissionConfig.profit_max >= profit,
            )
            .order_by(CommissionConfig.sort_order)
        )
        result = (await db.execute(stmt)).scalars().first()
        if result:
            return result
        fallback_stmt = (
            select(CommissionConfig)
            .where(
                CommissionConfig.agent_id.is_(None),
                CommissionConfig.profit_min <= profit,
                CommissionConfig.profit_max >= profit,
            )
            .order_by(CommissionConfig.sort_order)
        )
        return (await db.execute(fallback_stmt)).scalars().first()
