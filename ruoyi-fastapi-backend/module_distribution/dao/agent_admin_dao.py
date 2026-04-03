from collections.abc import Sequence

from sqlalchemy import Select, and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.role_do import SysRole
from module_admin.entity.do.user_do import SysUser
from module_distribution.entity.do.agent_info_do import AgentInfo
from module_distribution.entity.vo.agent_admin_vo import AssignL1AgentModel


class AgentAdminDao:
    """
    代理分销后台管理数据库操作层
    """

    @classmethod
    async def get_agent_info_by_agent_id(cls, db: AsyncSession, agent_id: int) -> AgentInfo | None:
        return (await db.execute(select(AgentInfo).where(AgentInfo.agent_id == agent_id))).scalars().first()

    @classmethod
    async def get_agent_info_by_user_id(cls, db: AsyncSession, user_id: int) -> AgentInfo | None:
        return (await db.execute(select(AgentInfo).where(AgentInfo.user_id == user_id))).scalars().first()

    @classmethod
    async def get_agent_info_by_code(cls, db: AsyncSession, agent_code: str) -> AgentInfo | None:
        return (await db.execute(select(AgentInfo).where(AgentInfo.agent_code == agent_code))).scalars().first()

    @classmethod
    async def get_distribution_role_by_key(cls, db: AsyncSession, role_key: str) -> SysRole | None:
        stmt = select(SysRole).where(SysRole.role_key == role_key, SysRole.status == '0', SysRole.del_flag == '0')
        return (await db.execute(stmt)).scalars().first()

    @classmethod
    async def add_agent_info_dao(cls, db: AsyncSession, payload: AssignL1AgentModel) -> AgentInfo:
        payload_dict = payload.model_dump()
        entity = AgentInfo(
            user_id=payload_dict['user_id'],
            parent_agent_id=payload_dict.get('parent_agent_id'),
            agent_code=payload_dict['agent_code'],
            agent_level=payload_dict.get('agent_level', 1),
            bet_commission_rate=payload_dict['bet_commission_rate'],
            can_create_sub=0,
            status='0',
            remark=payload_dict.get('remark'),
            create_time=payload_dict.get('create_time'),
            update_time=payload_dict.get('update_time'),
        )
        db.add(entity)
        await db.flush()
        return entity

    @classmethod
    async def update_agent_permission_dao(cls, db: AsyncSession, agent_id: int, can_create_sub: int) -> None:
        await db.execute(update(AgentInfo).where(AgentInfo.agent_id == agent_id).values(can_create_sub=can_create_sub))

    @classmethod
    async def update_agent_status_dao(cls, db: AsyncSession, agent_id: int, status: str) -> None:
        await db.execute(update(AgentInfo).where(AgentInfo.agent_id == agent_id).values(status=status))

    @classmethod
    async def update_agent_commission_rate_dao(cls, db: AsyncSession, agent_id: int, bet_commission_rate: float) -> None:
        await db.execute(
            update(AgentInfo).where(AgentInfo.agent_id == agent_id).values(bet_commission_rate=bet_commission_rate)
        )

    @classmethod
    async def batch_update_agent_status_dao(cls, db: AsyncSession, agent_ids: list[int], status: str) -> None:
        if not agent_ids:
            return
        await db.execute(update(AgentInfo).where(AgentInfo.agent_id.in_(agent_ids)).values(status=status))

    @classmethod
    async def update_user_agent_flags_dao(
        cls,
        db: AsyncSession,
        user_id: int,
        *,
        agent_level: int | None = None,
        belong_agent_id: int | None = None,
        can_create_sub_agent: int | None = None,
    ) -> None:
        values = {}
        if agent_level is not None:
            values['agent_level'] = agent_level
        if can_create_sub_agent is not None:
            values['can_create_sub_agent'] = can_create_sub_agent
        values['belong_agent_id'] = belong_agent_id
        await db.execute(update(SysUser).where(SysUser.user_id == user_id).values(**values))

    @classmethod
    async def update_user_status_dao(cls, db: AsyncSession, user_id: int, status: str) -> None:
        await db.execute(update(SysUser).where(SysUser.user_id == user_id).values(status=status))

    @classmethod
    async def batch_update_user_status_dao(cls, db: AsyncSession, user_ids: list[int], status: str) -> None:
        if not user_ids:
            return
        await db.execute(update(SysUser).where(SysUser.user_id.in_(user_ids)).values(status=status))

    @classmethod
    async def get_agent_detail_row(cls, db: AsyncSession, agent_id: int) -> tuple[AgentInfo, SysUser] | None:
        stmt = (
            select(AgentInfo, SysUser)
            .join(SysUser, and_(AgentInfo.user_id == SysUser.user_id, SysUser.del_flag == '0'))
            .where(AgentInfo.agent_id == agent_id)
        )
        return (await db.execute(stmt)).first()

    @classmethod
    async def get_agent_tree_rows(cls, db: AsyncSession) -> Sequence[tuple[AgentInfo, SysUser]]:
        stmt: Select = (
            select(AgentInfo, SysUser)
            .join(SysUser, and_(AgentInfo.user_id == SysUser.user_id, SysUser.del_flag == '0'))
            .order_by(AgentInfo.agent_level, AgentInfo.agent_id)
        )
        return (await db.execute(stmt)).all()

    @classmethod
    async def get_direct_child_agents(cls, db: AsyncSession, parent_agent_id: int) -> Sequence[AgentInfo]:
        stmt = select(AgentInfo).where(AgentInfo.parent_agent_id == parent_agent_id)
        return (await db.execute(stmt)).scalars().all()

    @classmethod
    async def get_direct_customers(cls, db: AsyncSession, belong_agent_id: int) -> Sequence[SysUser]:
        stmt = select(SysUser).where(
            SysUser.del_flag == '0', SysUser.belong_agent_id == belong_agent_id, SysUser.agent_level == 0
        )
        return (await db.execute(stmt)).scalars().all()

    @classmethod
    async def get_direct_agent_rows(
        cls,
        db: AsyncSession,
        parent_agent_id: int | None,
    ) -> Sequence[tuple[AgentInfo, SysUser]]:
        stmt = (
            select(AgentInfo, SysUser)
            .join(SysUser, and_(AgentInfo.user_id == SysUser.user_id, SysUser.del_flag == '0'))
            .where(AgentInfo.parent_agent_id == parent_agent_id)
            .order_by(AgentInfo.agent_id.desc())
        )
        return (await db.execute(stmt)).all()

    @classmethod
    async def get_direct_customer_rows(
        cls,
        db: AsyncSession,
        belong_agent_id: int | None,
    ) -> Sequence[SysUser]:
        stmt = (
            select(SysUser)
            .where(SysUser.del_flag == '0', SysUser.belong_agent_id == belong_agent_id, SysUser.agent_level == 0)
            .order_by(SysUser.user_id.desc())
        )
        return (await db.execute(stmt)).scalars().all()

    @classmethod
    async def get_customers_by_agent_ids(cls, db: AsyncSession, belong_agent_ids: list[int]) -> Sequence[SysUser]:
        if not belong_agent_ids:
            return []
        stmt = (
            select(SysUser)
            .where(SysUser.del_flag == '0', SysUser.belong_agent_id.in_(belong_agent_ids), SysUser.agent_level == 0)
            .order_by(SysUser.user_id.desc())
        )
        return (await db.execute(stmt)).scalars().all()
