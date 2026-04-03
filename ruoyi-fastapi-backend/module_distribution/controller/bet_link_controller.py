from typing import Annotated

from fastapi import Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_distribution.entity.vo.bet_vo import (
    BetLinkListQueryModel,
    BetLinkRowModel,
    BetOpenPreviewModel,
    ConfirmBetModel,
    ConfirmBetResultModel,
    ConfirmLinkResultModel,
    CreateBetLinkModel,
    MyBetRowModel,
)
from module_distribution.service.bet_service import BetService
from utils.log_util import logger
from utils.response_util import ResponseUtil

bet_link_controller = APIRouterPro(
    prefix='/bet', order_num=21, tags=['代理分销-投注管理'], dependencies=[PreAuthDependency()]
)


@bet_link_controller.post(
    '/link/create',
    summary='创建投注链接接口',
    description='总代理创建投注链接',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('bet:link:manage')],
)
@Log(title='代理分销-创建投注链接', business_type=BusinessType.INSERT)
async def create_bet_link(
    request: Request,
    body: CreateBetLinkModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await BetService.create_bet_link_services(request, query_db, current_user, body)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message, data=result.result)


@bet_link_controller.get(
    '/link/list',
    summary='获取投注链接列表接口',
    description='总代理获取自己创建的投注链接列表',
    response_model=PageResponseModel[BetLinkRowModel],
    dependencies=[UserInterfaceAuthDependency('bet:link:manage')],
)
async def get_bet_link_list(
    request: Request,
    query_object: Annotated[BetLinkListQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await BetService.get_bet_link_list_services(query_db, current_user, query_object)
    logger.info('获取投注链接列表成功')
    return ResponseUtil.success(model_content=result)


@bet_link_controller.get(
    '/open/{token}',
    summary='打开投注链接接口',
    description='用户打开投注链接查看预览',
    response_model=DataResponseModel[BetOpenPreviewModel],
)
async def open_bet_link(
    request: Request,
    token: Annotated[str, Path(description='投注链接token')],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await BetService.get_open_preview_services(request, query_db, current_user, token)
    logger.info('打开投注链接成功')
    return ResponseUtil.success(data=result)


@bet_link_controller.post(
    '/open/{token}/confirm',
    summary='确认投注接口',
    description='用户确认投注，确认后不可修改',
    response_model=DataResponseModel[ConfirmBetResultModel],
)
@Log(title='代理分销-确认投注', business_type=BusinessType.INSERT)
async def confirm_bet(
    request: Request,
    token: Annotated[str, Path(description='投注链接token')],
    body: ConfirmBetModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await BetService.confirm_bet_services(request, query_db, current_user, token, body)
    logger.info('确认投注成功')
    return ResponseUtil.success(data=result)


@bet_link_controller.put(
    '/link/{link_id}/confirm-result',
    summary='确认中奖结果接口',
    description='总代理确认中奖或未中奖结果并触发收益计算',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('bet:link:manage')],
)
@Log(title='代理分销-确认中奖结果', business_type=BusinessType.UPDATE)
async def confirm_link_result(
    request: Request,
    link_id: Annotated[int, Path(description='投注链接ID')],
    body: ConfirmLinkResultModel,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await BetService.confirm_link_result_services(request, query_db, current_user, link_id, body)
    logger.info(result.message)
    return ResponseUtil.success(msg=result.message)


@bet_link_controller.get(
    '/my-bets',
    summary='获取我的投注记录接口',
    description='当前登录用户获取自己的投注记录',
    response_model=DataResponseModel[list[MyBetRowModel]],
    dependencies=[UserInterfaceAuthDependency('bet:my:view')],
)
async def get_my_bets(
    request: Request,
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await BetService.get_my_bets_services(query_db, current_user)
    logger.info('获取我的投注记录成功')
    return ResponseUtil.success(data=result)
