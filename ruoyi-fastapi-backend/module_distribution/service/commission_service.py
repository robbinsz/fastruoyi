from sqlalchemy.ext.asyncio import AsyncSession

from common.vo import CrudResponseModel
from exceptions.exception import ServiceException
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_distribution.dao.agent_admin_dao import AgentAdminDao
from module_distribution.dao.commission_dao import CommissionDao
from module_distribution.entity.vo.commission_vo import (
    CommissionConfigItemModel,
    CommissionConfigResponseModel,
    SaveCommissionConfigModel,
)


class CommissionService:
    @classmethod
    async def _get_current_agent_id(cls, query_db: AsyncSession, current_user: CurrentUserModel) -> int | None:
        if current_user.user.admin:
            return None
        if not current_user.user.agent_level or current_user.user.agent_level <= 0:
            raise ServiceException(message='当前用户不是代理商，不能维护提成配置')
        current_agent = await AgentAdminDao.get_agent_info_by_user_id(query_db, current_user.user.user_id)
        if current_agent is None:
            raise ServiceException(message='当前代理信息不存在')
        return current_agent.agent_id

    @classmethod
    def _validate_items(cls, items: list[CommissionConfigItemModel]) -> None:
        if not items:
            raise ServiceException(message='提成配置不能为空')
        ordered_items = sorted(items, key=lambda item: item.sort_order)
        previous_max = None
        for item in ordered_items:
            if item.profit_min > item.profit_max:
                raise ServiceException(message='利润区间下限不能大于上限')
            if item.commission_amt < 0:
                raise ServiceException(message='固定提成金额不能小于0')
            if not 0 <= item.split_ratio <= 1:
                raise ServiceException(message='分成比例必须在0到1之间')
            if previous_max is not None and item.profit_min <= previous_max:
                raise ServiceException(message='利润区间不能重叠，请检查排序和区间范围')
            previous_max = item.profit_max

    @classmethod
    async def get_commission_config_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel
    ) -> CommissionConfigResponseModel:
        agent_id = await cls._get_current_agent_id(query_db, current_user)
        custom_rows = await CommissionDao.get_config_rows(query_db, agent_id) if agent_id is not None else []
        source_type = 'custom' if custom_rows else 'default'
        target_rows = custom_rows or await CommissionDao.get_config_rows(query_db, None)
        return CommissionConfigResponseModel(
            source_type=source_type,
            items=[
                CommissionConfigItemModel(
                    config_id=row.config_id,
                    profit_min=float(row.profit_min),
                    profit_max=float(row.profit_max),
                    commission_amt=float(row.commission_amt),
                    split_ratio=float(row.split_ratio),
                    sort_order=row.sort_order,
                )
                for row in target_rows
            ],
        )

    @classmethod
    async def save_commission_config_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel, payload: SaveCommissionConfigModel
    ) -> CrudResponseModel:
        agent_id = await cls._get_current_agent_id(query_db, current_user)
        if agent_id is None:
            raise ServiceException(message='超级管理员请使用平台默认配置接口')
        cls._validate_items(payload.items)
        await CommissionDao.clear_config_rows(query_db, agent_id)
        for item in sorted(payload.items, key=lambda row: row.sort_order):
            await CommissionDao.add_config_row_dao(
                query_db,
                {
                    'agent_id': agent_id,
                    'profit_min': item.profit_min,
                    'profit_max': item.profit_max,
                    'commission_amt': item.commission_amt,
                    'split_ratio': item.split_ratio,
                    'sort_order': item.sort_order,
                },
            )
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='保存个性化提成配置成功')

    @classmethod
    async def reset_commission_config_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel
    ) -> CrudResponseModel:
        agent_id = await cls._get_current_agent_id(query_db, current_user)
        if agent_id is None:
            raise ServiceException(message='超级管理员请使用平台默认配置接口')
        await CommissionDao.clear_config_rows(query_db, agent_id)
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='重置为平台默认配置成功')

    @classmethod
    async def update_default_commission_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel, payload: SaveCommissionConfigModel
    ) -> CrudResponseModel:
        if not current_user.user.admin:
            raise ServiceException(message='仅超级管理员可维护平台默认提成配置')
        cls._validate_items(payload.items)
        await CommissionDao.clear_config_rows(query_db, None)
        for item in sorted(payload.items, key=lambda row: row.sort_order):
            await CommissionDao.add_config_row_dao(
                query_db,
                {
                    'agent_id': None,
                    'profit_min': item.profit_min,
                    'profit_max': item.profit_max,
                    'commission_amt': item.commission_amt,
                    'split_ratio': item.split_ratio,
                    'sort_order': item.sort_order,
                },
            )
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='更新平台默认提成配置成功')
