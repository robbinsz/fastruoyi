from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank, Size


class AssignL1AgentModel(BaseModel):
    """
    分配总代理请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    user_id: int = Field(description='要提升为总代理的用户ID')
    agent_code: str = Field(description='代理商编码')
    parent_agent_id: int | None = Field(default=None, description='直属上级代理ID，总代理为空')
    agent_level: int = Field(default=1, description='代理层级')
    bet_commission_rate: float = Field(default=0.025, description='投注提成系数')
    remark: str | None = Field(default=None, description='备注')
    create_by: str | None = Field(default=None, description='创建者')
    update_by: str | None = Field(default=None, description='更新者')
    create_time: datetime | None = Field(default=None, description='创建时间')
    update_time: datetime | None = Field(default=None, description='更新时间')

    @NotBlank(field_name='agent_code', message='代理商编码不能为空')
    @Size(field_name='agent_code', min_length=1, max_length=50, message='代理商编码长度不能超过50个字符')
    def get_agent_code(self) -> str:
        return self.agent_code

    def validate_fields(self) -> None:
        self.get_agent_code()


class AgentPermissionModel(BaseModel):
    """
    代理授权响应模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    agent_id: int = Field(description='代理商ID')
    user_id: int = Field(description='关联用户ID')
    agent_code: str = Field(description='代理商编码')
    agent_level: int = Field(description='代理层级')
    can_create_sub: int = Field(description='是否允许创建次级代理')
    status: str = Field(description='状态')


class AgentDetailModel(BaseModel):
    """
    代理详情模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    agent_id: int = Field(description='代理商ID')
    user_id: int = Field(description='关联用户ID')
    user_name: str = Field(description='登录账号')
    nick_name: str = Field(description='用户昵称')
    phonenumber: str | None = Field(default=None, description='手机号')
    email: str | None = Field(default=None, description='邮箱')
    parent_agent_id: int | None = Field(default=None, description='直属上级代理ID')
    agent_code: str = Field(description='代理编码')
    agent_level: int = Field(description='代理层级')
    bet_commission_rate: float = Field(description='投注提成系数')
    can_create_sub: int = Field(description='是否允许创建次级代理')
    status: str = Field(description='状态')
    remark: str | None = Field(default=None, description='备注')
    create_time: datetime | None = Field(default=None, description='创建时间')


class AgentTreeNodeModel(BaseModel):
    """
    代理树节点模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    agent_id: int = Field(description='代理商ID')
    user_id: int = Field(description='用户ID')
    parent_agent_id: int | None = Field(default=None, description='父级代理ID')
    agent_code: str = Field(description='代理商编码')
    agent_level: int = Field(description='代理层级')
    agent_name: str = Field(description='用户昵称')
    user_name: str = Field(description='登录账号')
    can_create_sub: int = Field(description='是否可创建次级代理')
    status: str = Field(description='状态')
    children: list['AgentTreeNodeModel'] = Field(default_factory=list, description='下级代理')


class VisibleScopeModel(BaseModel):
    """
    当前用户可见范围模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    is_admin: bool = Field(description='是否超级管理员')
    self_user_id: int = Field(description='当前用户ID')
    self_agent_id: int | None = Field(default=None, description='当前代理ID')
    agent_level: int = Field(description='代理层级')
    direct_agent_ids: list[int] = Field(default_factory=list, description='直属下级代理ID')
    visible_agent_ids: list[int] = Field(default_factory=list, description='当前代理可见的全部代理ID')
    direct_customer_user_ids: list[int] = Field(default_factory=list, description='直属客户用户ID')
    visible_user_ids: list[int] = Field(default_factory=list, description='可见用户ID合集')


AgentTreeNodeModel.model_rebuild()
