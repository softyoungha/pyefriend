from sqlalchemy import Column, Integer, Text, String, JSON, Float, Index, ForeignKey, Boolean

from pyefriend.utils.orm_helper import provide_session
from pyefriend.utils.const import MarketCode
from .base import Base, Length


class Product(Base):
    __tablename__ = 'product'

    # columns
    code = Column(String(Length.ID), primary_key=True, comment='종목코드')
    name = Column(String(Length.ID), comment='종목명')
    market_code = Column(String(Length.TYPE), comment='마켓코드')

    __table_args__ = (
        Index('idx_product', name, unique=True),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Product(code='{self.code}', name='{self.name}')>"

    @property
    def as_dict(self):
        return {
            'product_code': self.code,
            'product_name': self.name,
            'market_code': self.market_code,
        }

    @classmethod
    @provide_session
    def list(cls, market: str = None, only_oversea: bool = False, session=None):
        query = session.query(cls)

        if only_oversea:
            return query.filter(cls.market_code != MarketCode.KRX).all()

        if market is None:
            return query.all()

        else:
            return query.filter(cls.market_code == market).all()
