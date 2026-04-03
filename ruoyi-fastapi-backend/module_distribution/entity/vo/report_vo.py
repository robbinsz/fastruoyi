from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class EarningsReportQueryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    start_date: date | None = Field(default=None, description='开始日期')
    end_date: date | None = Field(default=None, description='结束日期')
    period: str = Field(default='day', description='趋势聚合粒度：day/week/month')
    user_name: str | None = Field(default=None, description='用户账号')
    link_name: str | None = Field(default=None, description='链接名称')


class DashboardSummaryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    total_bet_amount: float = Field(default=0, description='总投注额')
    total_win_amount: float = Field(default=0, description='总中奖额')
    total_bet_commission: float = Field(default=0, description='投注提成')
    total_profit_commission: float = Field(default=0, description='利润提成')
    total_commission: float = Field(default=0, description='总收益')


class EarningsDetailRowModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_id: int = Field(description='用户ID')
    user_name: str = Field(description='用户账号')
    nick_name: str = Field(description='用户昵称')
    link_id: int = Field(description='链接ID')
    link_name: str | None = Field(default=None, description='链接名称')
    bet_amount: float = Field(default=0, description='投注金额')
    win_amount: float = Field(default=0, description='中奖金额')
    profit: float = Field(default=0, description='用户收益')
    confirm_time: datetime | None = Field(default=None, description='确认时间')


class TrendPointModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    stat_date: str = Field(description='统计日期')
    total_bet_amount: float = Field(default=0, description='总投注额')
    total_commission: float = Field(default=0, description='总收益')


class SubAgentSummaryRowModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    agent_id: int = Field(description='代理ID')
    agent_code: str = Field(description='代理编码')
    user_name: str = Field(description='登录账号')
    nick_name: str = Field(description='昵称')
    total_commission: float = Field(default=0, description='总收益')


class MyEarningsSummaryModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    total_bet_amount: float = Field(default=0, description='总投注额')
    total_win_amount: float = Field(default=0, description='总中奖额')
    total_profit: float = Field(default=0, description='总收益')


class MyEarningsResponseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    summary: MyEarningsSummaryModel = Field(description='汇总信息')
    rows: list[EarningsDetailRowModel] = Field(default_factory=list, description='明细列表')
