from typing import Annotated

from fastapi import Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_distribution.entity.vo.agent_admin_vo import AgentDetailModel
from module_distribution.entity.vo.agent_vo import (
    AgentListQueryModel,
    AgentMemberRowModel,
    CreateCustomerModel,
    CreateSubAgentModel,
    UpdateCommissionRateModel,
)
from module_distribution.service.agent_service import AgentService
from utils.log_util import logger
from utils.response_util import ResponseUtil

agent_controller = APIRouterPro(
    prefix='/agent', order_num=20, tags=['代理分销-代理管理'], dependencies=[PreAuthDependency()]
)


@agent_controller.get(
    '/direct-agents',
    summary='获取直属下级代理列表接口',
    description='当前代理查看直属一层下级代理',
    response_model=PageResponseModel[AgentMemberRowModel],
    dependencies=[UserInterfaceAuthDependency('agent:list')],
)
async def get_direct_agents(
    request: Request,
    query_object: Annotated[AgentListQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await AgentService.get_direct_agent_list_services(query_db, current_user, query_object)
    logger.info('获取直属下级代理列表成功')
    return ResponseUtil.success(model_content=result)


@agent_controller.get(
    '/direct-customers',
    summary='获取直属客户列表接口',
    description='当前代理查看直属客户',
    response_model=PageResponseModel[AgentMemberRowModel],
    dependencies=[UserInterfaceAuthDependency('agent:list')],
)
async def get_direct_customers(
    request: Request,
    query_object: Annotated[AgentListQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await AgentService.get_direct_customer_list_services(query_db, current_user, query_object)
    logger.info('获取直属客户列表成功')
    return ResponseUtil.success(model_content=result)


@agent_controller.post(
    '/create-customer',
    summary='创建直属客户接口',
    description='当前代理创建直属普通客户',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('agent:customer:manage')],
)
@Log(title='代理分销-创建直属客户', business_type=BusinessType.INSERT)
async def create_customer(
    request: Request,
    body: CreateCustomerModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await AgentService.create_customer_services(query_db, current_user, body)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@agent_controller.post(
    '/create-sub',
    summary='创建下级代理接口',
    description='当前代理创建直属一层下级代理',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('agent:create:sub')],
)
@Log(title='代理分销-创建下级代理', business_type=BusinessType.INSERT)
async def create_sub_agent(
    request: Request,
    body: CreateSubAgentModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await AgentService.create_sub_agent_services(query_db, current_user, body)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@agent_controller.get(
    '/{agent_id}',
    summary='获取代理详情接口',
    description='当前登录代理或超管查看代理详情，受DataScope限制',
    response_model=DataResponseModel[AgentDetailModel],
    dependencies=[UserInterfaceAuthDependency('agent:list')],
)
async def get_agent_detail(
    request: Request,
    agent_id: int,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await AgentService.get_agent_detail_services(query_db, current_user, agent_id)
    logger.info('获取代理详情成功')
    return ResponseUtil.success(data=result)


@agent_controller.put(
    '/{agent_id}/commission-rate',
    summary='代理修改自己的提成系数接口',
    description='代理只能修改自己的投注提成系数',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('agent:list')],
)
@Log(title='代理分销-修改自身提成系数', business_type=BusinessType.UPDATE)
async def update_self_commission_rate(
    request: Request,
    agent_id: int,
    body: UpdateCommissionRateModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await AgentService.update_self_commission_rate_services(query_db, current_user, agent_id, body)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
