import uuid
from datetime import datetime

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from common.constant import HttpStatusConstant
from common.vo import CrudResponseModel, PageModel
from exceptions.exception import ServiceException
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_distribution.dao.agent_admin_dao import AgentAdminDao
from module_distribution.dao.bet_dao import BetDao
from module_distribution.entity.do.bet_link_do import BetLink
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
from module_distribution.service.earnings_service import EarningsService
from utils.page_util import PageUtil


class BetService:
    """
    投注链接服务层
    """

    REDIS_PREFIX = 'bet_link'

    @classmethod
    def _normalize_expire_at(cls, expire_at: datetime) -> datetime:
        if expire_at.tzinfo is None:
            return expire_at
        return expire_at.astimezone().replace(tzinfo=None)

    @classmethod
    def _ensure_l1(cls, current_user: CurrentUserModel) -> None:
        if current_user.user.admin:
            return
        if current_user.user.agent_level != 1:
            raise ServiceException(message='仅总代理可执行该操作')

    @classmethod
    async def _get_current_agent_id(cls, query_db: AsyncSession, current_user: CurrentUserModel) -> int:
        if current_user.user.admin:
            raise ServiceException(message='当前接口暂不支持超级管理员直接操作，请使用总代理账号')

        agent = await AgentAdminDao.get_agent_info_by_user_id(query_db, current_user.user.user_id)
        if agent is None:
            raise ServiceException(message='当前总代理代理信息不存在')
        return agent.agent_id

    @classmethod
    def _normalize_link_status(cls, link: BetLink, confirmed_users: int) -> int:
        if link.confirm_result is not None:
            return 3
        if datetime.now() >= link.expire_at:
            return 2
        if link.max_users and confirmed_users >= link.max_users:
            return 2
        if confirmed_users > 0:
            return 1
        return 0

    @classmethod
    async def create_bet_link_services(
        cls, request: Request, query_db: AsyncSession, current_user: CurrentUserModel, payload: CreateBetLinkModel
    ) -> CrudResponseModel:
        payload.validate_fields()
        cls._ensure_l1(current_user)
        if payload.odds <= 0:
            raise ServiceException(message='赔率必须大于0')
        if payload.max_users is not None and payload.max_users <= 0:
            raise ServiceException(message='最大参与人数必须大于0')
        normalized_expire_at = cls._normalize_expire_at(payload.expire_at)
        if normalized_expire_at <= datetime.now():
            raise ServiceException(message='过期时间必须晚于当前时间')

        agent_id = await cls._get_current_agent_id(query_db, current_user)
        token = uuid.uuid4().hex
        link = await BetDao.add_bet_link_dao(
            query_db,
            {
                'link_token': token,
                'agent_id': agent_id,
                'link_name': payload.link_name,
                'bet_desc': payload.bet_desc,
                'odds': payload.odds,
                'expire_at': normalized_expire_at,
                'max_users': payload.max_users,
                'status': 0,
            },
        )
        link_id = link.link_id
        ttl = int((normalized_expire_at - datetime.now()).total_seconds())
        if ttl > 0:
            await request.app.state.redis.set(f'{cls.REDIS_PREFIX}:{token}', str(link_id), ex=ttl)
        await query_db.commit()
        return CrudResponseModel(
            is_success=True,
            message='创建投注链接成功',
            result={'linkId': link_id, 'token': token, 'url': f'/bet/link/{token}'},
        )

    @classmethod
    async def get_bet_link_list_services(
        cls, query_db: AsyncSession, current_user: CurrentUserModel, query_object: BetLinkListQueryModel
    ) -> PageModel[BetLinkRowModel]:
        if current_user.user.admin:
            return PageUtil.get_page_obj([], query_object.page_num, query_object.page_size)
        cls._ensure_l1(current_user)
        agent_id = await cls._get_current_agent_id(query_db, current_user)
        links = await BetDao.get_bet_link_list_by_agent(query_db, agent_id, query_object.link_name, query_object.status)
        rows = []
        for link in links:
            confirmed_users = await BetDao.count_confirmed_records_by_link(query_db, link.link_id)
            status = cls._normalize_link_status(link, confirmed_users)
            if status != link.status:
                await BetDao.update_bet_link_dao(query_db, link.link_id, status=status)
                link.status = status
            rows.append(
                BetLinkRowModel(
                    link_id=link.link_id,
                    link_token=link.link_token,
                    agent_id=link.agent_id,
                    link_name=link.link_name,
                    bet_desc=link.bet_desc,
                    odds=float(link.odds) if link.odds is not None else None,
                    expire_at=link.expire_at,
                    max_users=link.max_users,
                    status=link.status,
                    confirm_result=link.confirm_result,
                    confirm_time=link.confirm_time,
                    create_time=link.create_time,
                    confirmed_users=confirmed_users,
                )
            )
        await query_db.commit()
        return PageUtil.get_page_obj(rows, query_object.page_num, query_object.page_size)

    @classmethod
    async def get_open_preview_services(
        cls, request: Request, query_db: AsyncSession, current_user: CurrentUserModel, token: str
    ) -> BetOpenPreviewModel:
        link = await BetDao.get_bet_link_by_token(query_db, token)
        if link is None:
            redis_link_id = await request.app.state.redis.get(f'{cls.REDIS_PREFIX}:{token}')
            if redis_link_id:
                link = await BetDao.get_bet_link_by_id(query_db, int(redis_link_id))
        if link is None:
            raise ServiceException(message='投注链接已过期或不存在')

        confirmed_users = await BetDao.count_confirmed_records_by_link(query_db, link.link_id)
        status = cls._normalize_link_status(link, confirmed_users)
        if status != link.status:
            await BetDao.update_bet_link_dao(query_db, link.link_id, status=status)
            link.status = status
            await query_db.commit()

        record = await BetDao.get_bet_record_by_link_and_user(query_db, link.link_id, current_user.user.user_id)
        return BetOpenPreviewModel(
            link_id=link.link_id,
            link_name=link.link_name,
            bet_desc=link.bet_desc,
            odds=float(link.odds) if link.odds is not None else None,
            expire_at=link.expire_at,
            max_users=link.max_users,
            status=link.status,
            confirm_result=link.confirm_result,
            confirmed_users=confirmed_users,
            already_confirmed=bool(record and record.is_confirmed == 1),
            bet_amount=float(record.bet_amount) if record and record.bet_amount is not None else None,
            win_amount=float(record.win_amount) if record and record.win_amount is not None else None,
            round_profit=float(record.round_profit) if record and record.round_profit is not None else None,
        )

    @classmethod
    async def confirm_bet_services(
        cls,
        request: Request,
        query_db: AsyncSession,
        current_user: CurrentUserModel,
        token: str,
        payload: ConfirmBetModel,
    ) -> ConfirmBetResultModel:
        if payload.bet_amount <= 0:
            raise ServiceException(message='投注金额必须大于0')
        preview = await cls.get_open_preview_services(request, query_db, current_user, token)
        if preview.status in {2, 3}:
            raise ServiceException(message='投注链接已截止或已结算', status_code=HttpStatusConstant.CONFLICT)
        if preview.already_confirmed:
            raise ServiceException(message='同一用户对同一链接只能投注一次', status_code=HttpStatusConstant.CONFLICT)

        link = await BetDao.get_bet_link_by_id(query_db, preview.link_id)
        if link is None:
            raise ServiceException(message='投注链接不存在')
        now = datetime.now()
        record = await BetDao.add_bet_record_dao(
            query_db,
            {
                'link_id': link.link_id,
                'user_id': current_user.user.user_id,
                'belong_agent_id': current_user.user.belong_agent_id,
                'bet_amount': payload.bet_amount,
                'odds': float(link.odds),
                'is_confirmed': 1,
                'confirm_time': now,
                'win_amount': 0,
                'round_profit': 0,
            },
        )
        response_model = ConfirmBetResultModel(
            record_id=record.record_id,
            link_id=record.link_id,
            bet_amount=float(record.bet_amount),
            odds=float(record.odds),
            confirm_time=record.confirm_time,
        )
        confirmed_users = await BetDao.count_confirmed_records_by_link(query_db, link.link_id)
        status = cls._normalize_link_status(link, confirmed_users)
        await BetDao.update_bet_link_dao(query_db, link.link_id, status=status)
        await query_db.commit()
        return response_model

    @classmethod
    async def confirm_link_result_services(
        cls,
        request: Request,
        query_db: AsyncSession,
        current_user: CurrentUserModel,
        link_id: int,
        payload: ConfirmLinkResultModel,
    ) -> CrudResponseModel:
        cls._ensure_l1(current_user)
        agent_id = await cls._get_current_agent_id(query_db, current_user)
        link = await BetDao.get_bet_link_by_id(query_db, link_id)
        if link is None:
            raise ServiceException(message='投注链接不存在')
        if link.agent_id != agent_id:
            raise ServiceException(message='只能确认自己的投注链接')
        if link.confirm_result is not None:
            raise ServiceException(message='该投注链接已确认结果，不可再次修改', status_code=HttpStatusConstant.CONFLICT)
        if payload.is_win not in {0, 1}:
            raise ServiceException(message='开奖结果不合法')

        records = await BetDao.get_confirmed_records_by_link(query_db, link.link_id)
        for record in records:
            await BetDao.update_bet_record_dao(query_db, record.record_id, is_win=payload.is_win)

        await BetDao.update_bet_link_dao(
            query_db,
            link.link_id,
            confirm_result=payload.is_win,
            confirm_time=datetime.now(),
            status=3,
        )
        await EarningsService.calculate_for_link(query_db, link.link_id)
        await EarningsService.invalidate_dashboard_cache(request, query_db, agent_id)
        await request.app.state.redis.delete(f'{cls.REDIS_PREFIX}:{link.link_token}')
        await query_db.commit()
        return CrudResponseModel(is_success=True, message='确认中奖结果成功')

    @classmethod
    async def get_my_bets_services(cls, query_db: AsyncSession, current_user: CurrentUserModel) -> list[MyBetRowModel]:
        rows = await BetDao.get_my_bet_records(query_db, current_user.user.user_id)
        result = []
        for record, link in rows:
            result.append(
                MyBetRowModel(
                    record_id=record.record_id,
                    link_id=record.link_id,
                    link_name=link.link_name,
                    bet_amount=float(record.bet_amount),
                    odds=float(record.odds),
                    is_confirmed=record.is_confirmed,
                    is_win=record.is_win,
                    win_amount=float(record.win_amount) if record.win_amount is not None else None,
                    round_profit=float(record.round_profit) if record.round_profit is not None else None,
                    confirm_time=record.confirm_time,
                )
            )
        return result
