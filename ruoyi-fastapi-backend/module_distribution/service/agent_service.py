from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_admin.dao.user_dao import UserDao
from module_admin.entity.do.user_do import SysUser
from module_admin.entity.vo.user_vo import CurrentUserModel, UserModel, UserRoleModel
from module_admin.service.user_service import UserService
from module_distribution.dao.agent_admin_dao import AgentAdminDao
from module_distribution.entity.do.agent_info_do import AgentInfo
from module_distribution.entity.vo.agent_admin_vo import AgentDetailModel, AssignL1AgentModel
from module_distribution.entity.vo.agent_vo import (
    AgentListQueryModel,
    AgentMemberRowModel,
    CreateCustomerModel,
    CreateSubAgentModel,
    UpdateCommissionRateModel,
)
from module_distribution.service.agent_scope_service import AgentScopeService
from utils.page_util import PageUtil
from utils.pwd_util import PwdUtil


class AgentService:
    """
    代理管理服务层
    """

    ROLE_KEY_CUSTOMER = 'customer'
    MAX_AGENT_LEVEL = 4

    @classmethod
    def _ensure_agent_user_context(cls, current_user: CurrentUserModel) -> None:
        if current_user.user.admin:
            raise ServiceException(message='当前接口暂不支持超级管理员直接调用，请使用代理账号操作')
        if not current_user.user.agent_level or current_user.user.agent_level <= 0:
            raise ServiceException(message='当前用户不是代理商，不能执行此操作')

    @classmethod
    async def _get_current_agent_info(cls, query_db: AsyncSession, current_user: CurrentUserModel) -> AgentInfo:
        cls._ensure_agent_user_context(current_user)
        agent_info = await AgentAdminDao.get_agent_info_by_user_id(query_db, current_user.user.user_id)
        if agent_info is None:
            raise ServiceException(message='当前代理信息不存在')
        return agent_info

    @classmethod
    def _build_member_row_from_agent(cls, agent: AgentInfo, user: SysUser) -> AgentMemberRowModel:
        return AgentMemberRowModel(
            user_id=user.user_id,
            user_name=user.user_name,
            nick_name=user.nick_name,
            phonenumber=user.phonenumber,
            status=user.status,
            agent_level=user.agent_level or 0,
            belong_agent_id=user.belong_agent_id,
            can_create_sub_agent=user.can_create_sub_agent or 0,
            create_time=user.create_time,
            agent_id=agent.agent_id,
            parent_agent_id=agent.parent_agent_id,
            agent_code=agent.agent_code,
            bet_commission_rate=float(agent.bet_commission_rate) if agent.bet_commission_rate is not None else None,
        )

    @classmethod
    def _build_member_row_from_customer(cls, user: SysUser) -> AgentMemberRowModel:
        return AgentMemberRowModel(
            user_id=user.user_id,
            user_name=user.user_name,
            nick_name=user.nick_name,
            phonenumber=user.phonenumber,
            status=user.status,
            agent_level=user.agent_level or 0,
            belong_agent_id=user.belong_agent_id,
            can_create_sub_agent=user.can_create_sub_agent or 0,
            create_time=user.create_time,
            agent_id=None,
            parent_agent_id=None,
            agent_code=None,
            bet_commission_rate=None,
        )

    @classmethod
    async def get_direct_agent_list_services(
        cls,
        query_db: AsyncSession,
        current_user: CurrentUserModel,
        query_object: AgentListQueryModel,
    ) -> PageModel[AgentMemberRowModel]:
        scope = await AgentScopeService.get_visible_scope(query_db, current_user)
        parent_agent_id = scope.self_agent_id
        if current_user.user.admin:
            parent_agent_id = None
        elif not parent_agent_id:
            raise ServiceException(message='当前用户无代理上下文')
        rows = await AgentAdminDao.get_direct_agent_rows(query_db, parent_agent_id)
        result_rows = []
        for agent, user in rows:
            if query_object.user_name and query_object.user_name not in user.user_name:
                continue
            if query_object.nick_name and query_object.nick_name not in user.nick_name:
                continue
            if query_object.phonenumber and (not user.phonenumber or query_object.phonenumber not in user.phonenumber):
                continue
            if query_object.status and user.status != query_object.status:
                continue
            if query_object.agent_code and query_object.agent_code not in agent.agent_code:
                continue
            result_rows.append(cls._build_member_row_from_agent(agent, user))
        return PageUtil.get_page_obj(result_rows, query_object.page_num, query_object.page_size)

    @classmethod
    async def get_direct_customer_list_services(
        cls,
        query_db: AsyncSession,
        current_user: CurrentUserModel,
        query_object: AgentListQueryModel,
    ) -> PageModel[AgentMemberRowModel]:
        scope = await AgentScopeService.get_visible_scope(query_db, current_user)
        if current_user.user.admin:
            rows = []
        else:
            if not scope.self_agent_id:
                raise ServiceException(message='当前用户无代理上下文')
            rows = await AgentAdminDao.get_direct_customer_rows(query_db, scope.self_agent_id)
        result_rows = []
        for user in rows:
            if query_object.user_name and query_object.user_name not in user.user_name:
                continue
            if query_object.nick_name and query_object.nick_name not in user.nick_name:
                continue
            if query_object.phonenumber and (not user.phonenumber or query_object.phonenumber not in user.phonenumber):
                continue
            if query_object.status and user.status != query_object.status:
                continue
            result_rows.append(cls._build_member_row_from_customer(user))
        return PageUtil.get_page_obj(result_rows, query_object.page_num, query_object.page_size)

    @classmethod
    async def get_agent_detail_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel, agent_id: int
    ) -> AgentDetailModel:
        scope = await AgentScopeService.get_visible_scope(query_db, current_user)
        row = await AgentAdminDao.get_agent_detail_row(query_db, agent_id)
        if row is None:
            raise ServiceException(message='代理商不存在')
        agent_info, user = row
        if not current_user.user.admin and user.user_id not in set(scope.visible_user_ids):
            raise ServiceException(message='无权查看该代理详情')
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
    async def update_self_commission_rate_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel, agent_id: int, payload: UpdateCommissionRateModel
    ) -> CrudResponseModel:
        current_agent = await cls._get_current_agent_info(query_db, current_user)
        if current_agent.agent_id != agent_id:
            raise ServiceException(message='仅允许修改当前代理自己的提成系数')
        if payload.bet_commission_rate <= 0 or payload.bet_commission_rate >= 1:
            raise ServiceException(message='投注提成系数必须大于0且小于1')
        try:
            await AgentAdminDao.update_agent_commission_rate_dao(query_db, agent_id, payload.bet_commission_rate)
            await query_db.commit()
        except Exception as exc:
            await query_db.rollback()
            raise exc
        return CrudResponseModel(is_success=True, message='更新自己的提成系数成功')

    @classmethod
    async def create_customer_services(
        cls,
        query_db: AsyncSession,
        current_user: CurrentUserModel,
        payload: CreateCustomerModel,
    ) -> CrudResponseModel:
        payload.validate_fields()
        current_agent = await cls._get_current_agent_info(query_db, current_user)
        customer_role = await AgentAdminDao.get_distribution_role_by_key(query_db, cls.ROLE_KEY_CUSTOMER)
        if customer_role is None:
            raise ServiceException(message='缺少customer角色，请先执行初始化SQL')

        candidate = UserModel(
            userName=payload.user_name,
            nickName=payload.nick_name,
            email=payload.email,
            phonenumber=payload.phonenumber,
        )
        if not await UserService.check_user_name_unique_services(query_db, candidate):
            raise ServiceException(message=f'新增客户{payload.user_name}失败，登录账号已存在')
        if payload.phonenumber and not await UserService.check_phonenumber_unique_services(query_db, candidate):
            raise ServiceException(message=f'新增客户{payload.user_name}失败，手机号码已存在')
        if payload.email and not await UserService.check_email_unique_services(query_db, candidate):
            raise ServiceException(message=f'新增客户{payload.user_name}失败，邮箱账号已存在')

        now = datetime.now()
        user_payload = UserModel(
            deptId=payload.dept_id or current_user.user.dept_id,
            userName=payload.user_name,
            nickName=payload.nick_name,
            email=payload.email,
            phonenumber=payload.phonenumber,
            sex=payload.sex,
            password=PwdUtil.get_password_hash(payload.password),
            status='0',
            remark=payload.remark,
            agentLevel=0,
            belongAgentId=current_agent.agent_id,
            canCreateSubAgent=0,
            createBy=current_user.user.user_name,
            createTime=now,
            updateBy=current_user.user.user_name,
            updateTime=now,
        )
        try:
            user_entity = await UserDao.add_user_dao(query_db, user_payload)
            created_user_id = user_entity.user_id
            await UserDao.add_user_role_dao(
                query_db, UserRoleModel(userId=created_user_id, roleId=customer_role.role_id)
            )
            await query_db.commit()
        except Exception as exc:
            await query_db.rollback()
            raise exc

        return CrudResponseModel(is_success=True, message='创建直属客户成功', result={'userId': created_user_id})

    @classmethod
    async def create_sub_agent_services(
        cls,
        query_db: AsyncSession,
        current_user: CurrentUserModel,
        payload: CreateSubAgentModel,
    ) -> CrudResponseModel:
        payload.validate_fields()
        current_agent = await cls._get_current_agent_info(query_db, current_user)
        if current_user.user.can_create_sub_agent != 1:
            raise ServiceException(message='当前代理未被授权创建次级代理')
        next_level = (current_user.user.agent_level or 0) + 1
        if next_level > cls.MAX_AGENT_LEVEL:
            raise ServiceException(message='代理层级不能超过4级')
        if await AgentAdminDao.get_agent_info_by_code(query_db, payload.agent_code):
            raise ServiceException(message='代理商编码已存在')

        role_key = f'agent_l{next_level}'
        agent_role = await AgentAdminDao.get_distribution_role_by_key(query_db, role_key)
        if agent_role is None:
            raise ServiceException(message=f'缺少{role_key}角色，请先执行初始化SQL')

        candidate = UserModel(
            userName=payload.user_name,
            nickName=payload.nick_name,
            email=payload.email,
            phonenumber=payload.phonenumber,
        )
        if not await UserService.check_user_name_unique_services(query_db, candidate):
            raise ServiceException(message=f'新增代理{payload.user_name}失败，登录账号已存在')
        if payload.phonenumber and not await UserService.check_phonenumber_unique_services(query_db, candidate):
            raise ServiceException(message=f'新增代理{payload.user_name}失败，手机号码已存在')
        if payload.email and not await UserService.check_email_unique_services(query_db, candidate):
            raise ServiceException(message=f'新增代理{payload.user_name}失败，邮箱账号已存在')

        now = datetime.now()
        user_payload = UserModel(
            deptId=payload.dept_id or current_user.user.dept_id,
            userName=payload.user_name,
            nickName=payload.nick_name,
            email=payload.email,
            phonenumber=payload.phonenumber,
            sex=payload.sex,
            password=PwdUtil.get_password_hash(payload.password),
            status='0',
            remark=payload.remark,
            agentLevel=next_level,
            belongAgentId=current_agent.agent_id,
            canCreateSubAgent=0,
            createBy=current_user.user.user_name,
            createTime=now,
            updateBy=current_user.user.user_name,
            updateTime=now,
        )
        agent_payload = AssignL1AgentModel(
            user_id=0,
            agent_code=payload.agent_code,
            bet_commission_rate=payload.bet_commission_rate,
            remark=payload.remark,
            create_by=current_user.user.user_name,
            update_by=current_user.user.user_name,
            create_time=now,
            update_time=now,
        )
        try:
            user_entity = await UserDao.add_user_dao(query_db, user_payload)
            created_user_id = user_entity.user_id
            await UserDao.add_user_role_dao(
                query_db, UserRoleModel(userId=created_user_id, roleId=agent_role.role_id)
            )
            agent_payload_dict = agent_payload.model_copy(
                update={
                    'user_id': created_user_id,
                    'agent_level': next_level,
                    'parent_agent_id': current_agent.agent_id,
                }
            )
            await AgentAdminDao.add_agent_info_dao(query_db, agent_payload_dict)
            await query_db.commit()
        except Exception as exc:
            await query_db.rollback()
            raise exc

        return CrudResponseModel(is_success=True, message='创建下级代理成功', result={'userId': created_user_id})
