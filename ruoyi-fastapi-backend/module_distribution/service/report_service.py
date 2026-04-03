from __future__ import annotations

from typing import TYPE_CHECKING

from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_distribution.dao.agent_admin_dao import AgentAdminDao
from module_distribution.dao.report_dao import ReportDao
from module_distribution.entity.vo.report_vo import (
    DashboardSummaryModel,
    EarningsDetailRowModel,
    EarningsReportQueryModel,
    MyEarningsResponseModel,
    MyEarningsSummaryModel,
    SubAgentSummaryRowModel,
    TrendPointModel,
)
from module_distribution.service.agent_scope_service import AgentScopeService
from utils.common_util import bytes2file_response
from utils.excel_util import ExcelUtil
from utils.page_util import PageUtil

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from fastapi import Request
    from sqlalchemy.ext.asyncio import AsyncSession

    from module_admin.entity.do.user_do import SysUser
    from module_admin.entity.vo.user_vo import CurrentUserModel
    from module_distribution.entity.do.agent_info_do import AgentInfo
    from module_distribution.entity.do.bet_link_do import BetLink
    from module_distribution.entity.do.earnings_do import AgentEarnings, UserEarnings


class ReportService:
    EXPORT_LIMIT = 5000

    @classmethod
    def _build_dashboard_cache_key(cls, agent_id: int, query_object: EarningsReportQueryModel) -> str:
        start_date = query_object.start_date.isoformat() if query_object.start_date else 'all'
        end_date = query_object.end_date.isoformat() if query_object.end_date else 'all'
        return f'report:dashboard:{agent_id}:{start_date}:{end_date}'

    @classmethod
    def _sum_user_earnings(cls, rows: Sequence[tuple[UserEarnings, SysUser, BetLink]]) -> tuple[float, float]:
        total_bet_amount = sum(float(row[0].bet_amount) for row in rows)
        total_win_amount = sum(float(row[0].win_amount) for row in rows)
        return total_bet_amount, total_win_amount

    @classmethod
    def _sum_agent_earnings(cls, rows: Sequence[AgentEarnings]) -> tuple[float, float, float]:
        total_bet_commission = sum(float(row.bet_commission) for row in rows)
        total_profit_commission = sum(float(row.profit_commission) for row in rows)
        total_commission = sum(float(row.total_commission) for row in rows)
        return total_bet_commission, total_profit_commission, total_commission

    @classmethod
    def _build_period_key(cls, target_date: date, period: str) -> str:
        if period == 'month':
            return target_date.strftime('%Y-%m')
        if period == 'week':
            iso_year, iso_week, _ = target_date.isocalendar()
            return f'{iso_year}-W{iso_week:02d}'
        return target_date.isoformat()

    @classmethod
    async def get_dashboard_services(
        cls, request: Request, query_db: AsyncSession, current_user: CurrentUserModel, query_object: EarningsReportQueryModel
    ) -> DashboardSummaryModel:
        scope = await AgentScopeService.get_visible_scope(query_db, current_user)
        if scope.self_agent_id and hasattr(request.app.state, 'redis'):
            cache_key = cls._build_dashboard_cache_key(scope.self_agent_id, query_object)
            cached_value = await request.app.state.redis.get(cache_key)
            if cached_value:
                return DashboardSummaryModel.model_validate_json(cached_value)
        user_rows = await ReportDao.get_user_earnings_rows(
            query_db, scope.visible_user_ids, query_object.start_date, query_object.end_date
        )
        agent_ids = scope.visible_agent_ids or [agent_id for agent_id in [scope.self_agent_id, *scope.direct_agent_ids] if agent_id]
        agent_rows = await ReportDao.get_agent_earnings_rows(
            query_db, agent_ids, query_object.start_date, query_object.end_date
        )
        total_bet_amount, total_win_amount = cls._sum_user_earnings(user_rows)
        total_bet_commission, total_profit_commission, total_commission = cls._sum_agent_earnings(agent_rows)
        result = DashboardSummaryModel(
            total_bet_amount=total_bet_amount,
            total_win_amount=total_win_amount,
            total_bet_commission=total_bet_commission,
            total_profit_commission=total_profit_commission,
            total_commission=total_commission,
        )
        if scope.self_agent_id and hasattr(request.app.state, 'redis'):
            await request.app.state.redis.set(
                cls._build_dashboard_cache_key(scope.self_agent_id, query_object),
                result.model_dump_json(),
                ex=300,
            )
        return result

    @classmethod
    async def get_earnings_list_services(
        cls,
        query_db: AsyncSession,
        current_user: CurrentUserModel,
        query_object: EarningsReportQueryModel,
    ) -> PageModel[EarningsDetailRowModel]:
        scope = await AgentScopeService.get_visible_scope(query_db, current_user)
        rows = await ReportDao.get_user_earnings_rows(
            query_db,
            scope.visible_user_ids,
            query_object.start_date,
            query_object.end_date,
            query_object.user_name,
            query_object.link_name,
        )
        result = [
            EarningsDetailRowModel(
                user_id=user.user_id,
                user_name=user.user_name,
                nick_name=user.nick_name,
                link_id=earning.link_id,
                link_name=link.link_name,
                bet_amount=float(earning.bet_amount),
                win_amount=float(earning.win_amount),
                profit=float(earning.profit),
                confirm_time=earning.confirm_time,
            )
            for earning, user, link in rows
        ]
        return PageUtil.get_page_obj(result, query_object.page_num, query_object.page_size)

    @classmethod
    async def get_trend_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel, query_object: EarningsReportQueryModel
    ) -> list[TrendPointModel]:
        scope = await AgentScopeService.get_visible_scope(query_db, current_user)
        user_rows = await ReportDao.get_user_earnings_rows(
            query_db, scope.visible_user_ids, query_object.start_date, query_object.end_date
        )
        agent_ids = scope.visible_agent_ids or [agent_id for agent_id in [scope.self_agent_id, *scope.direct_agent_ids] if agent_id]
        agent_rows = await ReportDao.get_agent_earnings_rows(
            query_db, agent_ids, query_object.start_date, query_object.end_date
        )
        trend_map = {}
        for earning, _, _ in user_rows:
            if not earning.confirm_time:
                continue
            stat_date = cls._build_period_key(earning.confirm_time.date(), query_object.period)
            trend_map.setdefault(stat_date, {'bet': 0.0, 'commission': 0.0})
            trend_map[stat_date]['bet'] += float(earning.bet_amount)
        for earning in agent_rows:
            if not earning.create_time:
                continue
            stat_date = cls._build_period_key(earning.create_time.date(), query_object.period)
            trend_map.setdefault(stat_date, {'bet': 0.0, 'commission': 0.0})
            trend_map[stat_date]['commission'] += float(earning.total_commission)
        return [
            TrendPointModel(stat_date=stat_date, total_bet_amount=values['bet'], total_commission=values['commission'])
            for stat_date, values in sorted(trend_map.items())
        ]

    @classmethod
    async def get_sub_agents_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel, query_object: EarningsReportQueryModel
    ) -> list[SubAgentSummaryRowModel]:
        scope = await AgentScopeService.get_visible_scope(query_db, current_user)
        if not scope.direct_agent_ids:
            return []
        agent_rows = await ReportDao.get_agent_earnings_rows(
            query_db, scope.direct_agent_ids, query_object.start_date, query_object.end_date
        )
        agent_info_rows: Sequence[tuple[AgentInfo, SysUser]] = await ReportDao.get_sub_agent_rows(
            query_db, scope.direct_agent_ids
        )
        earnings_map = {}
        for row in agent_rows:
            earnings_map.setdefault(row.agent_id, 0.0)
            earnings_map[row.agent_id] += float(row.total_commission)
        return [
            SubAgentSummaryRowModel(
                agent_id=agent.agent_id,
                agent_code=agent.agent_code,
                user_name=user.user_name,
                nick_name=user.nick_name,
                total_commission=earnings_map.get(agent.agent_id, 0.0),
            )
            for agent, user in agent_info_rows
        ]

    @classmethod
    async def export_earnings_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel, query_object: EarningsReportQueryModel
    ) -> CrudResponseModel:
        rows = await cls.get_earnings_list_services(query_db, current_user, query_object)
        if rows.total > cls.EXPORT_LIMIT:
            raise ServiceException(message='单次导出最多5000条，请缩短日期范围后重试')
        list_data = [row.model_dump(by_alias=True) for row in rows.rows]
        mapping_dict = {
            'userName': '用户账号',
            'nickName': '用户昵称',
            'linkName': '链接名称',
            'betAmount': '投注金额',
            'winAmount': '中奖金额',
            'profit': '用户收益',
            'confirmTime': '确认时间',
        }
        binary_data = ExcelUtil.export_list2excel(list_data, mapping_dict)
        file_agent_code = 'customer'
        if current_user.user.agent_level and current_user.user.agent_level > 0:
            current_agent = await AgentAdminDao.get_agent_info_by_user_id(query_db, current_user.user.user_id)
            if current_agent:
                file_agent_code = current_agent.agent_code
        start_date = query_object.start_date.isoformat() if query_object.start_date else 'all'
        end_date = query_object.end_date.isoformat() if query_object.end_date else 'all'
        filename = f'代理收益明细_{file_agent_code}_{start_date}_{end_date}.xlsx'
        return CrudResponseModel(
            is_success=True,
            message='导出成功',
            result={'content': bytes2file_response(binary_data), 'filename': filename},
        )

    @classmethod
    async def get_my_earnings_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel, query_object: EarningsReportQueryModel
    ) -> MyEarningsResponseModel:
        rows = await ReportDao.get_user_earnings_rows(
            query_db, [current_user.user.user_id], query_object.start_date, query_object.end_date
        )
        detail_rows = [
            EarningsDetailRowModel(
                user_id=user.user_id,
                user_name=user.user_name,
                nick_name=user.nick_name,
                link_id=earning.link_id,
                link_name=link.link_name,
                bet_amount=float(earning.bet_amount),
                win_amount=float(earning.win_amount),
                profit=float(earning.profit),
                confirm_time=earning.confirm_time,
            )
            for earning, user, link in rows
        ]
        total_bet_amount, total_win_amount = cls._sum_user_earnings(rows)
        total_profit = sum(item.profit for item in detail_rows)
        return MyEarningsResponseModel(
            summary=MyEarningsSummaryModel(
                total_bet_amount=total_bet_amount,
                total_win_amount=total_win_amount,
                total_profit=total_profit,
            ),
            rows=detail_rows,
        )
