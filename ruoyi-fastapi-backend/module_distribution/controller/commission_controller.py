from typing import Annotated

from fastapi import Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_distribution.entity.vo.commission_vo import CommissionConfigResponseModel, SaveCommissionConfigModel
from module_distribution.service.commission_service import CommissionService
from utils.log_util import logger
from utils.response_util import ResponseUtil

commission_controller = APIRouterPro(
    prefix='/commission', order_num=23, tags=['代理分销-提成配置'], dependencies=[PreAuthDependency()]
)


@commission_controller.get(
    '/config',
    response_model=DataResponseModel[CommissionConfigResponseModel],
    dependencies=[UserInterfaceAuthDependency('commission:config')],
)
async def get_commission_config(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await CommissionService.get_commission_config_services(query_db, current_user)
    logger.info('获取提成配置成功')
    return ResponseUtil.success(data=result)


@commission_controller.put(
    '/config',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('commission:config')],
)
@Log(title='代理分销-保存个性化提成配置', business_type=BusinessType.UPDATE)
async def save_commission_config(
    request: Request,
    body: SaveCommissionConfigModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await CommissionService.save_commission_config_services(query_db, current_user, body)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@commission_controller.delete(
    '/config/reset',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('commission:config')],
)
@Log(title='代理分销-重置个性化提成配置', business_type=BusinessType.DELETE)
async def reset_commission_config(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await CommissionService.reset_commission_config_services(query_db, current_user)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@commission_controller.put(
    '/default',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('commission:default')],
)
@Log(title='代理分销-更新平台默认提成配置', business_type=BusinessType.UPDATE)
async def update_default_commission(
    request: Request,
    body: SaveCommissionConfigModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await CommissionService.update_default_commission_services(query_db, current_user, body)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)
