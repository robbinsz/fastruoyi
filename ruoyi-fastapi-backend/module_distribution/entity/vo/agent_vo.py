from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import Network, NotBlank, Size


class AgentListQueryModel(BaseModel):
    """
    代理/客户列表分页查询模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    user_name: str | None = Field(default=None, description='用户账号')
    nick_name: str | None = Field(default=None, description='用户昵称')
    phonenumber: str | None = Field(default=None, description='手机号')
    status: Literal['0', '1'] | None = Field(default=None, description='状态')
    agent_code: str | None = Field(default=None, description='代理编码，仅代理列表使用')


class AgentMemberRowModel(BaseModel):
    """
    代理成员列表行模型
    """

    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    user_id: int = Field(description='用户ID')
    user_name: str = Field(description='登录账号')
    nick_name: str = Field(description='用户昵称')
    phonenumber: str | None = Field(default=None, description='手机号')
    status: str | None = Field(default=None, description='状态')
    agent_level: int = Field(description='代理层级')
    belong_agent_id: int | None = Field(default=None, description='直属上级代理ID')
    can_create_sub_agent: int = Field(description='是否可创建次级代理')
    create_time: datetime | None = Field(default=None, description='创建时间')
    agent_id: int | None = Field(default=None, description='代理商ID')
    parent_agent_id: int | None = Field(default=None, description='父级代理ID')
    agent_code: str | None = Field(default=None, description='代理商编码')
    bet_commission_rate: float | None = Field(default=None, description='投注提成系数')


class CreateCustomerModel(BaseModel):
    """
    创建直属客户请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_name: str = Field(description='登录账号')
    nick_name: str = Field(description='用户昵称')
    password: str = Field(description='密码')
    phonenumber: str | None = Field(default=None, description='手机号')
    email: str | None = Field(default=None, description='邮箱')
    sex: Literal['0', '1', '2'] | None = Field(default='0', description='性别')
    dept_id: int | None = Field(default=None, description='部门ID，默认继承当前用户')
    remark: str | None = Field(default=None, description='备注')

    @NotBlank(field_name='user_name', message='用户账号不能为空')
    @Size(field_name='user_name', min_length=1, max_length=30, message='用户账号长度不能超过30个字符')
    def get_user_name(self) -> str:
        return self.user_name

    @NotBlank(field_name='nick_name', message='用户昵称不能为空')
    @Size(field_name='nick_name', min_length=1, max_length=30, message='用户昵称长度不能超过30个字符')
    def get_nick_name(self) -> str:
        return self.nick_name

    @Size(field_name='phonenumber', min_length=0, max_length=11, message='手机号码长度不能超过11个字符')
    def get_phonenumber(self) -> str | None:
        return self.phonenumber

    @Network(field_name='email', field_type='EmailStr', message='邮箱格式不正确')
    @Size(field_name='email', min_length=0, max_length=50, message='邮箱长度不能超过50个字符')
    def get_email(self) -> str | None:
        return self.email

    def validate_fields(self) -> None:
        self.get_user_name()
        self.get_nick_name()
        self.get_phonenumber()
        self.get_email()


class CreateSubAgentModel(CreateCustomerModel):
    """
    创建下级代理请求模型
    """

    agent_code: str = Field(description='代理商编码')
    bet_commission_rate: float = Field(default=0.025, description='投注提成系数')

    @NotBlank(field_name='agent_code', message='代理商编码不能为空')
    @Size(field_name='agent_code', min_length=1, max_length=50, message='代理商编码长度不能超过50个字符')
    def get_agent_code(self) -> str:
        return self.agent_code

    def validate_fields(self) -> None:
        super().validate_fields()
        self.get_agent_code()


class UpdateCommissionRateModel(BaseModel):
    """
    修改提成系数请求模型
    """

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    bet_commission_rate: float = Field(description='投注提成系数')
