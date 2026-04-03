from datetime import datetime

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from module_distribution.dao.agent_admin_dao import AgentAdminDao
from module_distribution.dao.bet_dao import BetDao


class EarningsService:
    """
    收益计算服务
    """

    @classmethod
    async def _collect_affected_agent_ids(cls, query_db: AsyncSession, agent_id: int) -> list[int]:
        affected_ids = [agent_id]
        current_agent_id = agent_id
        while current_agent_id:
            current_agent = await AgentAdminDao.get_agent_info_by_agent_id(query_db, current_agent_id)
            if current_agent is None or not current_agent.parent_agent_id:
                break
            affected_ids.append(current_agent.parent_agent_id)
            current_agent_id = current_agent.parent_agent_id
        return list(dict.fromkeys(affected_ids))

    @classmethod
    async def invalidate_dashboard_cache(cls, request: Request, query_db: AsyncSession, agent_id: int) -> None:
        if not hasattr(request.app.state, 'redis'):
            return
        redis_client = request.app.state.redis
        for affected_agent_id in await cls._collect_affected_agent_ids(query_db, agent_id):
            keys = await redis_client.keys(f'report:dashboard:{affected_agent_id}:*')
            if keys:
                await redis_client.delete(*keys)

    @classmethod
    async def calculate_for_link(cls, query_db: AsyncSession, link_id: int) -> None:
        records = await BetDao.get_confirmed_records_by_link(query_db, link_id)
        for record in records:
            bet_amount = float(record.bet_amount)
            odds = float(record.odds)
            win_amount = bet_amount * odds if record.is_win == 1 else 0.0
            round_profit = win_amount - bet_amount
            await BetDao.update_bet_record_dao(
                query_db,
                record.record_id,
                win_amount=win_amount,
                round_profit=round_profit,
            )
            await BetDao.add_user_earning_dao(
                query_db,
                {
                    'user_id': record.user_id,
                    'belong_agent_id': record.belong_agent_id,
                    'link_id': record.link_id,
                    'bet_amount': bet_amount,
                    'win_amount': win_amount,
                    'profit': round_profit,
                    'confirm_time': datetime.now(),
                },
            )

            direct_agent = await BetDao.get_agent_info_by_id(query_db, record.belong_agent_id)
            if direct_agent is None:
                continue

            bet_commission = bet_amount * float(direct_agent.bet_commission_rate)
            profit_commission = 0.0
            parent_share = 0.0

            if round_profit > 0:
                config = await BetDao.get_commission_config_for_agent(query_db, direct_agent.agent_id, round_profit)
                if config:
                    commission_amt = float(config.commission_amt)
                    profit_commission = commission_amt * float(config.split_ratio)
                    parent_share = commission_amt * (1 - float(config.split_ratio))

            total_commission = bet_commission + profit_commission
            await BetDao.add_agent_earning_dao(
                query_db,
                {
                    'agent_id': direct_agent.agent_id,
                    'source_user_id': record.user_id,
                    'link_id': record.link_id,
                    'total_bet_amt': bet_amount,
                    'user_profit': round_profit,
                    'earn_type': 'direct',
                    'bet_commission': bet_commission,
                    'profit_commission': profit_commission,
                    'total_commission': total_commission,
                },
            )

            if parent_share > 0 and direct_agent.parent_agent_id:
                await BetDao.add_agent_earning_dao(
                    query_db,
                    {
                        'agent_id': direct_agent.parent_agent_id,
                        'source_user_id': record.user_id,
                        'link_id': record.link_id,
                        'total_bet_amt': bet_amount,
                        'user_profit': round_profit,
                        'earn_type': 'inherit',
                        'bet_commission': 0,
                        'profit_commission': parent_share,
                        'total_commission': parent_share,
                    },
                )
