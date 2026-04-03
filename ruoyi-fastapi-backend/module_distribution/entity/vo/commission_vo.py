from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CommissionConfigItemModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    config_id: int | None = Field(default=None, description='配置ID')
    profit_min: float = Field(description='利润区间下限（含）')
    profit_max: float = Field(description='利润区间上限（含）')
    commission_amt: float = Field(description='固定提成金额')
    split_ratio: float = Field(description='当前代理分成比例')
    sort_order: int = Field(default=1, description='排序')


class CommissionConfigResponseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    source_type: str = Field(description='配置来源：custom/default')
    items: list[CommissionConfigItemModel] = Field(default_factory=list, description='提成配置明细')


class SaveCommissionConfigModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[CommissionConfigItemModel] = Field(default_factory=list, description='待保存配置')
