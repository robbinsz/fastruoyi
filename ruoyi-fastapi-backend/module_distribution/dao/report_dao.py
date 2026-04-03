from collections.abc import Sequence
from datetime import date, datetime, time

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.user_do import SysUser
from module_distribution.entity.do.agent_info_do import AgentInfo
from module_distribution.entity.do.bet_link_do import BetLink
from module_distribution.entity.do.earnings_do import AgentEarnings, UserEarnings


class ReportDao:
    @classmethod
    def _build_datetime_range(
        cls, start_date: date | None, end_date: date | None
    ) -> tuple[datetime | None, datetime | None]:
        begin = datetime.combine(start_date, time.min) if start_date else None
        end = datetime.combine(end_date, time.max) if end_date else None
        return begin, end

    @classmethod
    async def get_user_earnings_rows(
        cls,
        db: AsyncSession,
        visible_user_ids: list[int],
        start_date: date | None = None,
        end_date: date | None = None,
        user_name: str | None = None,
        link_name: str | None = None,
    ) -> Sequence[tuple[UserEarnings, SysUser, BetLink]]:
        begin, end = cls._build_datetime_range(start_date, end_date)
        stmt = (
            select(UserEarnings, SysUser, BetLink)
            .join(SysUser, UserEarnings.user_id == SysUser.user_id)
            .join(BetLink, UserEarnings.link_id == BetLink.link_id)
            .where(
                UserEarnings.user_id.in_(visible_user_ids) if visible_user_ids else False,
                UserEarnings.confirm_time >= begin if begin else True,
                UserEarnings.confirm_time <= end if end else True,
                SysUser.user_name.like(f'%{user_name}%') if user_name else True,
                BetLink.link_name.like(f'%{link_name}%') if link_name else True,
            )
            .order_by(UserEarnings.confirm_time.desc(), UserEarnings.earning_id.desc())
        )
        return (await db.execute(stmt)).all()

    @classmethod
    async def get_agent_earnings_rows(
        cls,
        db: AsyncSession,
        agent_ids: list[int],
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Sequence[AgentEarnings]:
        begin, end = cls._build_datetime_range(start_date, end_date)
        stmt = select(AgentEarnings).where(
            AgentEarnings.agent_id.in_(agent_ids) if agent_ids else False,
            AgentEarnings.create_time >= begin if begin else True,
            AgentEarnings.create_time <= end if end else True,
        )
        return (await db.execute(stmt)).scalars().all()

    @classmethod
    async def get_sub_agent_rows(cls, db: AsyncSession, agent_ids: list[int]) -> Sequence[tuple[AgentInfo, SysUser]]:
        stmt = (
            select(AgentInfo, SysUser)
            .join(SysUser, and_(AgentInfo.user_id == SysUser.user_id, SysUser.del_flag == '0'))
            .where(AgentInfo.agent_id.in_(agent_ids) if agent_ids else False)
        )
        return (await db.execute(stmt)).all()
