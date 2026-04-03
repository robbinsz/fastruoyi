from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Integer, Numeric, SmallInteger, String, Text

from config.database import Base


class BetLink(Base):
    """
    投注链接表
    """

    __tablename__ = 'bet_link'
    __table_args__ = {'comment': '投注链接表'}

    link_id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True, comment='投注链接ID')
    link_token = Column(String(64), nullable=False, unique=True, comment='链接唯一Token')
    agent_id = Column(BigInteger, nullable=False, comment='创建链接的总代理agent_id')
    link_name = Column(String(100), nullable=True, comment='链接名称')
    bet_desc = Column(Text, nullable=True, comment='投注说明')
    odds = Column(Numeric(6, 2), nullable=True, comment='赔率')
    expire_at = Column(DateTime, nullable=False, comment='过期时间')
    max_users = Column(Integer, nullable=True, comment='最大参与人数')
    status = Column(SmallInteger, nullable=False, server_default='0', comment='0=待投注 1=投注中 2=已截止 3=已结算')
    confirm_result = Column(SmallInteger, nullable=True, comment='开奖结果：0=未中 1=已中')
    confirm_time = Column(DateTime, nullable=True, comment='确认时间')
    create_time = Column(DateTime, nullable=True, default=datetime.now(), comment='创建时间')
