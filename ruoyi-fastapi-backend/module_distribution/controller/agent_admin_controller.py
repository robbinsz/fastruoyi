from typing import Annotated

from fastapi import Path, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_distribution.entity.vo.agent_admin_vo import AgentDetailModel, AgentPermissionModel, AgentTreeNodeModel
from module_distribution.service.agent_admin_service import AgentAdminService
from utils.log_util import logger
from utils.response_util import ResponseUtil


class AssignL1AgentRequestModel(BaseModel):
    """
    分配总代理请求
    """

    model_config = ConfigDict(alias_generator=to_camel)

    user_id: int = Field(description='用户ID')
    agent_code: str = Field(description='代理商编码')
    bet_commission_rate: float = Field(default=0.025, description='投注提成系数')
    remark: str | None = Field(default=None, description='备注')


class UpdateAgentStatusRequestModel(BaseModel):
    """
    修改代理状态请求
    """

    model_config = ConfigDict(alias_generator=to_camel)

    status: str = Field(description='状态：0=正常 1=停用')


class UpdateAgentCommissionRateRequestModel(BaseModel):
    """
    修改代理提成系数请求
    """

    model_config = ConfigDict(alias_generator=to_camel)

    bet_commission_rate: float = Field(description='投注提成系数')


agent_admin_controller = APIRouterPro(
    prefix='/admin', order_num=19, tags=['代理分销-超管管理'], dependencies=[PreAuthDependency()]
)


@agent_admin_controller.post(
    '/assign-l1-agent',
    summary='超管分配总代理接口',
    description='将已有用户分配为L1总代理',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('admin:assign:agent')],
)
@Log(title='代理分销-分配总代理', business_type=BusinessType.INSERT)
async def assign_l1_agent(
    request: Request,
    body: AssignL1AgentRequestModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    payload = AgentAdminService.build_assign_payload(
        user_id=body.user_id,
        agent_code=body.agent_code,
        bet_commission_rate=body.bet_commission_rate,
        remark=body.remark,
        operator=current_user.user.user_name,
    )
    result = await AgentAdminService.assign_l1_agent_services(query_db, payload)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@agent_admin_controller.put(
    '/grant-sub-agent/{agent_id}',
    summary='授权代理创建次级接口',
    description='超管授权指定代理可创建次级代理',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('admin:agent:grant')],
)
@Log(title='代理分销-授权次级代理', business_type=BusinessType.UPDATE)
async def grant_sub_agent_permission(
    request: Request,
    agent_id: Annotated[int, Path(description='代理商ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await AgentAdminService.update_sub_agent_permission_services(query_db, agent_id, 1)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@agent_admin_controller.put(
    '/revoke-sub-agent/{agent_id}',
    summary='撤销代理创建次级接口',
    description='超管撤销指定代理创建次级代理权限',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('admin:agent:grant')],
)
@Log(title='代理分销-撤销次级代理权限', business_type=BusinessType.UPDATE)
async def revoke_sub_agent_permission(
    request: Request,
    agent_id: Annotated[int, Path(description='代理商ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await AgentAdminService.update_sub_agent_permission_services(query_db, agent_id, 0)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@agent_admin_controller.get(
    '/agent-tree',
    summary='获取代理树接口',
    description='超管查看全部代理树结构',
    response_model=DataResponseModel[list[AgentTreeNodeModel]],
    dependencies=[UserInterfaceAuthDependency('admin:agent:tree')],
)
async def get_agent_tree(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await AgentAdminService.get_agent_tree_services(query_db)
    logger.info('获取代理树成功')
    return ResponseUtil.success(data=result)


@agent_admin_controller.get(
    '/agent-permission/{agent_id}',
    summary='获取代理授权详情接口',
    description='获取指定代理的授权详情',
    response_model=DataResponseModel[AgentPermissionModel],
    dependencies=[UserInterfaceAuthDependency(['admin:agent:tree', 'admin:agent:grant'])],
)
async def get_agent_permission_detail(
    request: Request,
    agent_id: Annotated[int, Path(description='代理商ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await AgentAdminService.get_agent_permission_detail_services(query_db, agent_id)
    logger.info('获取代理授权详情成功')
    return ResponseUtil.success(data=result)


@agent_admin_controller.get(
    '/agent-detail/{agent_id}',
    summary='获取代理详情接口',
    description='超管查看指定代理的详细信息',
    response_model=DataResponseModel[AgentDetailModel],
    dependencies=[UserInterfaceAuthDependency(['admin:agent:tree', 'admin:agent:edit'])],
)
async def get_agent_detail(
    request: Request,
    agent_id: Annotated[int, Path(description='代理商ID')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await AgentAdminService.get_agent_detail_services(query_db, agent_id)
    logger.info('获取代理详情成功')
    return ResponseUtil.success(data=result)


@agent_admin_controller.put(
    '/agent/{agent_id}/status',
    summary='更新代理状态接口',
    description='超管启用或停用代理',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('admin:agent:edit')],
)
@Log(title='代理分销-更新代理状态', business_type=BusinessType.UPDATE)
async def update_agent_status(
    request: Request,
    agent_id: Annotated[int, Path(description='代理商ID')],
    body: UpdateAgentStatusRequestModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await AgentAdminService.update_agent_status_services(query_db, agent_id, body.status)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@agent_admin_controller.put(
    '/agent/{agent_id}/commission-rate',
    summary='更新代理提成系数接口',
    description='超管修改代理投注提成系数',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('admin:agent:edit')],
)
@Log(title='代理分销-更新代理提成系数', business_type=BusinessType.UPDATE)
async def update_agent_commission_rate(
    request: Request,
    agent_id: Annotated[int, Path(description='代理商ID')],
    body: UpdateAgentCommissionRateRequestModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    result = await AgentAdminService.update_agent_commission_rate_services(query_db, agent_id, body.bet_commission_rate)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
