from typing import Annotated
from urllib.parse import quote

from fastapi import Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_distribution.entity.vo.report_vo import (
    DashboardSummaryModel,
    EarningsDetailRowModel,
    EarningsReportQueryModel,
    MyEarningsResponseModel,
    SubAgentSummaryRowModel,
    TrendPointModel,
)
from module_distribution.service.report_service import ReportService
from utils.log_util import logger
from utils.response_util import ResponseUtil

report_controller = APIRouterPro(
    prefix='/report', order_num=22, tags=['代理分销-收益报表'], dependencies=[PreAuthDependency()]
)


@report_controller.get(
    '/dashboard',
    response_model=DataResponseModel[DashboardSummaryModel],
    dependencies=[UserInterfaceAuthDependency('earnings:view')],
)
async def get_dashboard(
    request: Request,
    query_object: Annotated[EarningsReportQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await ReportService.get_dashboard_services(request, query_db, current_user, query_object)
    logger.info('获取收益看板成功')
    return ResponseUtil.success(data=result)


@report_controller.get(
    '/earnings/list',
    response_model=PageResponseModel[EarningsDetailRowModel],
    dependencies=[UserInterfaceAuthDependency('earnings:view')],
)
async def get_earnings_list(
    request: Request,
    query_object: Annotated[EarningsReportQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await ReportService.get_earnings_list_services(query_db, current_user, query_object)
    logger.info('获取收益明细成功')
    return ResponseUtil.success(model_content=result)


@report_controller.get(
    '/earnings/trend',
    response_model=DataResponseModel[list[TrendPointModel]],
    dependencies=[UserInterfaceAuthDependency('earnings:view')],
)
async def get_earnings_trend(
    request: Request,
    query_object: Annotated[EarningsReportQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await ReportService.get_trend_services(query_db, current_user, query_object)
    logger.info('获取收益趋势成功')
    return ResponseUtil.success(data=result)


@report_controller.get(
    '/sub-agents',
    response_model=DataResponseModel[list[SubAgentSummaryRowModel]],
    dependencies=[UserInterfaceAuthDependency('earnings:view')],
)
async def get_sub_agents(
    request: Request,
    query_object: Annotated[EarningsReportQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await ReportService.get_sub_agents_services(query_db, current_user, query_object)
    logger.info('获取直属下级代理汇总成功')
    return ResponseUtil.success(data=result)


@report_controller.get(
    '/earnings/export', response_class=StreamingResponse, dependencies=[UserInterfaceAuthDependency('earnings:view')]
)
async def export_earnings(
    request: Request,
    query_object: Annotated[EarningsReportQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await ReportService.export_earnings_services(query_db, current_user, query_object)
    logger.info(result.message)
    filename = result.result['filename']
    encoded_filename = quote(filename)
    return ResponseUtil.streaming(
        data=result.result['content'],
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Content-Disposition': f"attachment; filename=earnings.xlsx; filename*=UTF-8''{encoded_filename}"
        },
    )


@report_controller.get(
    '/my-earnings',
    response_model=DataResponseModel[MyEarningsResponseModel],
    dependencies=[UserInterfaceAuthDependency('earnings:my')],
)
async def get_my_earnings(
    request: Request,
    query_object: Annotated[EarningsReportQueryModel, Query()],
    query_db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    result = await ReportService.get_my_earnings_services(query_db, current_user, query_object)
    logger.info('获取我的收益成功')
    return ResponseUtil.success(data=result)
