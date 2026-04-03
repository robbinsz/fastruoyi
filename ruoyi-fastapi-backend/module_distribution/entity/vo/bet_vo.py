from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


class CreateBetLinkModel(BaseModel):
    """
    创建投注链接请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    link_name: str = Field(description='链接名称')
    bet_desc: str | None = Field(default=None, description='投注说明')
    odds: float = Field(description='赔率')
    expire_at: datetime = Field(description='过期时间')
    max_users: int | None = Field(default=None, description='最大参与人数')
    remark: str | None = Field(default=None, description='备注')

    @NotBlank(field_name='link_name', message='链接名称不能为空')
    @Size(field_name='link_name', min_length=1, max_length=100, message='链接名称长度不能超过100个字符')
    def get_link_name(self) -> str:
        return self.link_name

    def validate_fields(self) -> None:
        self.get_link_name()


class BetLinkRowModel(BaseModel):
    """
    投注链接列表行模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    link_id: int = Field(description='链接ID')
    link_token: str = Field(description='链接token')
    agent_id: int = Field(description='总代理agent_id')
    link_name: str | None = Field(default=None, description='链接名称')
    bet_desc: str | None = Field(default=None, description='投注说明')
    odds: float | None = Field(default=None, description='赔率')
    expire_at: datetime = Field(description='过期时间')
    max_users: int | None = Field(default=None, description='最大参与人数')
    status: int = Field(description='状态')
    confirm_result: int | None = Field(default=None, description='开奖结果')
    confirm_time: datetime | None = Field(default=None, description='确认时间')
    create_time: datetime | None = Field(default=None, description='创建时间')
    confirmed_users: int = Field(default=0, description='已参与人数')


class BetLinkListQueryModel(BaseModel):
    """
    投注链接分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    link_name: str | None = Field(default=None, description='链接名称')
    status: int | None = Field(default=None, description='状态')


class BetOpenPreviewModel(BaseModel):
    """
    链接打开预览模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    link_id: int = Field(description='链接ID')
    link_name: str | None = Field(default=None, description='链接名称')
    bet_desc: str | None = Field(default=None, description='投注说明')
    odds: float | None = Field(default=None, description='赔率')
    expire_at: datetime = Field(description='过期时间')
    max_users: int | None = Field(default=None, description='最大参与人数')
    status: int = Field(description='状态')
    confirm_result: int | None = Field(default=None, description='开奖结果')
    confirmed_users: int = Field(default=0, description='已参与人数')
    already_confirmed: bool = Field(default=False, description='当前用户是否已确认投注')
    bet_amount: float | None = Field(default=None, description='当前用户已投注金额')
    win_amount: float | None = Field(default=None, description='中奖金额')
    round_profit: float | None = Field(default=None, description='本轮收益')


class ConfirmBetModel(BaseModel):
    """
    用户确认投注请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    bet_amount: float = Field(description='投注金额')


class ConfirmBetResultModel(BaseModel):
    """
    用户确认投注响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    record_id: int = Field(description='投注记录ID')
    link_id: int = Field(description='链接ID')
    bet_amount: float = Field(description='投注金额')
    odds: float = Field(description='赔率')
    confirm_time: datetime | None = Field(default=None, description='确认时间')


class ConfirmLinkResultModel(BaseModel):
    """
    确认开奖结果请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    is_win: int = Field(description='开奖结果：0=未中 1=已中')


class MyBetRowModel(BaseModel):
    """
    我的投注记录行模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    record_id: int = Field(description='投注记录ID')
    link_id: int = Field(description='链接ID')
    link_name: str | None = Field(default=None, description='链接名称')
    bet_amount: float = Field(description='投注金额')
    odds: float = Field(description='赔率')
    is_confirmed: int = Field(description='是否已确认')
    is_win: int | None = Field(default=None, description='是否中奖')
    win_amount: float | None = Field(default=None, description='中奖金额')
    round_profit: float | None = Field(default=None, description='本轮收益')
    confirm_time: datetime | None = Field(default=None, description='确认时间')
