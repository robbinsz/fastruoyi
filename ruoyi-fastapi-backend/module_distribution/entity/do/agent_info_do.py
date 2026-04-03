from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Numeric, SmallInteger, String

from config.database import Base
from config.env import DataBaseConfig
from utils.common_util import SqlalchemyUtil


class AgentInfo(Base):
    """
    代理商扩展信息表
    """

    __tablename__ = 'agent_info'
    __table_args__ = {'comment': '代理商扩展信息表'}

    agent_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='代理商ID')
    user_id = Column(BigInteger, nullable=False, unique=True, comment='关联sys_user.user_id')
    parent_agent_id = Column(
        BigInteger,
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type, False),
        comment='直属上级代理商ID，总代理为空',
    )
    agent_code = Column(String(50), nullable=False, unique=True, comment='代理商编码')
    agent_level = Column(
        SmallInteger, nullable=False, server_default='1', comment='1=总代理 2=高级代理 3=中级代理 4=初级代理'
    )
    bet_commission_rate = Column(
        Numeric(5, 4), nullable=False, server_default='0.0250', comment='投注提成系数，例如0.0250'
    )
    can_create_sub = Column(SmallInteger, nullable=False, server_default='0', comment='是否可创建次级代理：0=否 1=是')
    status = Column(String(1), nullable=False, server_default='0', comment='状态：0=正常 1=停用')
    remark = Column(
        String(500),
        nullable=True,
        server_default=SqlalchemyUtil.get_server_default_null(DataBaseConfig.db_type),
        comment='备注',
    )
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
    update_time = Column(DateTime, nullable=True, default=datetime.now(), comment='更新时间')
