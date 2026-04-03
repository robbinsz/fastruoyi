from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class CommissionConfig(Base):
    """
    梯度提成配置表
    """

    __tablename__ = 'commission_config'
    __table_args__ = {'comment': '梯度提成配置表'}

    config_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    agent_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='代理商ID，空表示平台默认配置',
    )
    profit_min = Column(Numeric(12, 2), nullable=False, comment='利润区间下限（含）')
    profit_max = Column(Numeric(12, 2), nullable=False, comment='利润区间上限（含）')
    commission_amt = Column(Numeric(12, 2), nullable=False, comment='该区间固定提成金额')
    split_ratio = Column(Numeric(5, 4), nullable=False, server_default='0.5000', comment='本级代理分成比例')
    sort_order = Column(Integer, nullable=False, server_default='1', comment='排序序号')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')
