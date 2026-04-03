from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Numeric, SmallInteger, UniqueConstraint

from config.database import Base


class BetRecord(Base):
    """
    投注记录表
    """

    __tablename__ = 'bet_record'
    __table_args__ = (UniqueConstraint('link_id', 'user_id', name='uk_link_user'), {'comment': '投注记录表'})

    record_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='投注记录ID')
    link_id = Column(BigInteger, nullable=False, comment='关联投注链接')
    user_id = Column(BigInteger, nullable=False, comment='投注用户ID')
    belong_agent_id = Column(BigInteger, nullable=False, comment='用户直属代理商ID')
    bet_amount = Column(Numeric(12, 2), nullable=False, comment='投注金额')
    odds = Column(Numeric(6, 2), nullable=False, comment='确认时锁定赔率')
    is_confirmed = Column(SmallInteger, nullable=False, server_default='0', comment='是否已确认投注')
    confirm_time = Column(DateTime, nullable=True, comment='确认投注时间')
    is_win = Column(SmallInteger, nullable=True, comment='是否中奖：0=未中 1=已中')
    win_amount = Column(Numeric(12, 2), nullable=True, server_default='0', comment='中奖金额快照')
    round_profit = Column(Numeric(12, 2), nullable=True, server_default='0', comment='本轮收益快照')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
