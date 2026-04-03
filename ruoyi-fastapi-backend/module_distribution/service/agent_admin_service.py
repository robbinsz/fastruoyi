from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel
from exceptions.exception import ServiceException
from module_admin.dao.user_dao import UserDao
from module_admin.entity.vo.user_vo import UserRoleModel
from module_distribution.dao.agent_admin_dao import AgentAdminDao
from module_distribution.entity.vo.agent_admin_vo import (
    AgentDetailModel,
    AgentPermissionModel,
    AgentTreeNodeModel,
    AssignL1AgentModel,
)
from module_distribution.service.agent_scope_service import AgentScopeService


class AgentAdminService:
    """
    代理分销后台管理服务层
    """

    AGENT_ROLE_L1 = 'agent_l1'
    AGENT_ROLE_KEYS = ['agent_l1', 'agent_l2', 'agent_l3', 'agent_l4', 'customer']
    MAX_AGENT_LEVEL = 4

    @classmethod
    def _validate_bet_commission_rate(cls, bet_commission_rate: float) -> None:
        if bet_commission_rate <= 0 or bet_commission_rate >= 1:
            raise ServiceException(message='投注提成系数必须大于0且小于1')

    @classmethod
    async def assign_l1_agent_services(cls, query_db: AsyncSession, payload: AssignL1AgentModel) -> CrudResponseModel:
        user = await UserDao.get_user_by_id(query_db, payload.user_id)
        user_info = user.get('user_basic_info')
        if user_info is None or user_info.del_flag != '0':
            raise ServiceException(message='目标用户不存在')
        if user_info.user_id == 1:
            raise ServiceException(message='超级管理员不能被分配为总代理')
        if user_info.agent_level and user_info.agent_level > 0:
            raise ServiceException(message='该用户已是代理商，无需重复分配')
        if await AgentAdminDao.get_agent_info_by_code(query_db, payload.agent_code):
            raise ServiceException(message='代理商编码已存在')
        if await AgentAdminDao.get_agent_info_by_user_id(query_db, payload.user_id):
            raise ServiceException(message='该用户已绑定代理信息')

        role = await AgentAdminDao.get_distribution_role_by_key(query_db, cls.AGENT_ROLE_L1)
        if role is None:
            raise ServiceException(message='缺少agent_l1角色，请先执行初始化SQL')

        try:
            for role_key in cls.AGENT_ROLE_KEYS:
                distribution_role = await AgentAdminDao.get_distribution_role_by_key(query_db, role_key)
                if distribution_role:
                    await UserDao.delete_user_role_by_user_and_role_dao(
                        query_db, UserRoleModel(userId=payload.user_id, roleId=distribution_role.role_id)
                    )
            role_detail = await UserDao.get_user_role_detail(
                query_db, UserRoleModel(userId=payload.user_id, roleId=role.role_id)
            )
            if role_detail is None:
                await UserDao.add_user_role_dao(query_db, UserRoleModel(userId=payload.user_id, roleId=role.role_id))
            await AgentAdminDao.update_user_agent_flags_dao(
                query_db,
                payload.user_id,
                agent_level=1,
                belong_agent_id=None,
                can_create_sub_agent=0,
            )
            await AgentAdminDao.add_agent_info_dao(query_db, payload)
            await query_db.commit()
        except Exception as exc:
            await query_db.rollback()
            raise exc

        return CrudResponseModel(is_success=True, message='分配总代理成功')

    @classmethod
    async def update_sub_agent_permission_services(
        cls, query_db: AsyncSession, agent_id: int, can_create_sub: int
    ) -> CrudResponseModel:
        agent_info = await AgentAdminDao.get_agent_info_by_agent_id(query_db, agent_id)
        if agent_info is None:
            raise ServiceException(message='代理商不存在')
        if agent_info.agent_level >= cls.MAX_AGENT_LEVEL and can_create_sub == 1:
            raise ServiceException(message='初级代理不能被授权创建次级代理')

        try:
            await AgentAdminDao.update_agent_permission_dao(query_db, agent_id, can_create_sub)
            await AgentAdminDao.update_user_agent_flags_dao(
                query_db,
                agent_info.user_id,
                belong_agent_id=agent_info.parent_agent_id,
                can_create_sub_agent=can_create_sub,
            )
            await query_db.commit()
        except Exception as exc:
            await query_db.rollback()
            raise exc

        message = '授权创建次级代理成功' if can_create_sub == 1 else '撤销创建次级代理权限成功'
        return CrudResponseModel(is_success=True, message=message)

    @classmethod
    async def get_agent_permission_detail_services(cls, query_db: AsyncSession, agent_id: int) -> AgentPermissionModel:
        agent_info = await AgentAdminDao.get_agent_info_by_agent_id(query_db, agent_id)
        if agent_info is None:
            raise ServiceException(message='代理商不存在')
        return AgentPermissionModel(
            agent_id=agent_info.agent_id,
            user_id=agent_info.user_id,
            agent_code=agent_info.agent_code,
            agent_level=agent_info.agent_level,
            can_create_sub=agent_info.can_create_sub,
            status=agent_info.status,
        )

    @classmethod
    async def get_agent_detail_services(cls, query_db: AsyncSession, agent_id: int) -> AgentDetailModel:
        row = await AgentAdminDao.get_agent_detail_row(query_db, agent_id)
        if row is None:
            raise ServiceException(message='代理商不存在')
        agent_info, user = row
        return AgentDetailModel(
            agent_id=agent_info.agent_id,
            user_id=agent_info.user_id,
            user_name=user.user_name,
            nick_name=user.nick_name,
            phonenumber=user.phonenumber,
            email=user.email,
            parent_agent_id=agent_info.parent_agent_id,
            agent_code=agent_info.agent_code,
            agent_level=agent_info.agent_level,
            bet_commission_rate=float(agent_info.bet_commission_rate),
            can_create_sub=agent_info.can_create_sub,
            status=agent_info.status,
            remark=agent_info.remark,
            create_time=agent_info.create_time,
        )

    @classmethod
    async def update_agent_status_services(cls, query_db: AsyncSession, agent_id: int, status: str) -> CrudResponseModel:
        if status not in {'0', '1'}:
            raise ServiceException(message='状态值非法')
        agent_info = await AgentAdminDao.get_agent_info_by_agent_id(query_db, agent_id)
        if agent_info is None:
            raise ServiceException(message='代理商不存在')
        try:
            descendant_agent_ids, descendant_agent_user_ids, customer_user_ids = await AgentScopeService.collect_descendant_scope(
                query_db, agent_id
            )
            await AgentAdminDao.batch_update_agent_status_dao(query_db, [agent_id, *descendant_agent_ids], status)
            await AgentAdminDao.batch_update_user_status_dao(
                query_db,
                [agent_info.user_id, *descendant_agent_user_ids, *customer_user_ids],
                status,
            )
            await query_db.commit()
        except Exception as exc:
            await query_db.rollback()
            raise exc
        message = '启用代理及下级账号成功' if status == '0' else '停用代理及下级账号成功'
        return CrudResponseModel(is_success=True, message=message)

    @classmethod
    async def update_agent_commission_rate_services(
        cls, query_db: AsyncSession, agent_id: int, bet_commission_rate: float
    ) -> CrudResponseModel:
        cls._validate_bet_commission_rate(bet_commission_rate)
        agent_info = await AgentAdminDao.get_agent_info_by_agent_id(query_db, agent_id)
        if agent_info is None:
            raise ServiceException(message='代理商不存在')
        try:
            await AgentAdminDao.update_agent_commission_rate_dao(query_db, agent_id, bet_commission_rate)
            await query_db.commit()
        except Exception as exc:
            await query_db.rollback()
            raise exc
        return CrudResponseModel(is_success=True, message='更新代理提成系数成功')

    @classmethod
    async def get_agent_tree_services(cls, query_db: AsyncSession) -> list[AgentTreeNodeModel]:
        rows = await AgentAdminDao.get_agent_tree_rows(query_db)
        nodes = {}
        roots: list[AgentTreeNodeModel] = []
        for agent, user in rows:
            nodes[agent.agent_id] = AgentTreeNodeModel(
                agent_id=agent.agent_id,
                user_id=agent.user_id,
                parent_agent_id=agent.parent_agent_id,
                agent_code=agent.agent_code,
                agent_level=agent.agent_level,
                agent_name=user.nick_name,
                user_name=user.user_name,
                can_create_sub=agent.can_create_sub,
                status=agent.status,
                children=[],
            )

        for node in nodes.values():
            if node.parent_agent_id and node.parent_agent_id in nodes:
                nodes[node.parent_agent_id].children.append(node)
            else:
                roots.append(node)

        return roots

    @classmethod
    def build_assign_payload(
        cls,
        *,
        user_id: int,
        agent_code: str,
        bet_commission_rate: float,
        remark: str | None,
        operator: str,
    ) -> AssignL1AgentModel:
        now = datetime.now()
        return AssignL1AgentModel(
            user_id=user_id,
            agent_code=agent_code,
            bet_commission_rate=bet_commission_rate,
            remark=remark,
            create_by=operator,
            update_by=operator,
            create_time=now,
            update_time=now,
        )
