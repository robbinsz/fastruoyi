from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Numeric, String, UniqueConstraint

from config.database import Base


class UserEarnings(Base):
    """
    用户收益快照表
    """

    __tablename__ = 'user_earnings'
    __table_args__ = (UniqueConstraint('user_id', 'link_id', name='uk_user_link'), {'comment': '用户收益快照表'})

    earning_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    belong_agent_id = Column(BigInteger, nullable=False, comment='用户直属代理商ID')
    link_id = Column(BigInteger, nullable=False, comment='关联投注链接')
    bet_amount = Column(Numeric(12, 2), nullable=False, server_default='0', comment='投注金额')
    win_amount = Column(Numeric(12, 2), nullable=False, server_default='0', comment='中奖金额')
    profit = Column(Numeric(12, 2), nullable=False, server_default='0', comment='用户收益')
    confirm_time = Column(DateTime, nullable=True, comment='确认时间')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')


class AgentEarnings(Base):
    """
    代理收益记录表
    """

    __tablename__ = 'agent_earnings'
    __table_args__ = (
        UniqueConstraint('agent_id', 'source_user_id', 'link_id', name='uk_agent_user_link'),
        {'comment': '代理收益记录表'},
    )

    earning_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='主键ID')
    agent_id = Column(BigInteger, nullable=False, comment='获得收益的代理商ID')
    source_user_id = Column(BigInteger, nullable=False, comment='产生收益的源用户ID')
    link_id = Column(BigInteger, nullable=False, comment='关联投注链接')
    total_bet_amt = Column(Numeric(12, 2), nullable=False, server_default='0', comment='总投注金额')
    user_profit = Column(Numeric(12, 2), nullable=False, server_default='0', comment='用户利润')
    earn_type = Column(String(20), nullable=False, comment='收益类型：direct/inherit')
    bet_commission = Column(Numeric(12, 2), nullable=False, server_default='0', comment='投注提成')
    profit_commission = Column(Numeric(12, 2), nullable=False, server_default='0', comment='利润提成')
    total_commission = Column(Numeric(12, 2), nullable=False, server_default='0', comment='总佣金')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
