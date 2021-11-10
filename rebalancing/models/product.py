from typing import List, Dict, Union
from sqlalchemy import Column, Integer, Text, String, JSON, Float, Index, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref, Session

from rebalancing.utils.orm_helper import provide_session
from rebalancing.utils.const import MarketCode
from .base import Base, Length


class Product(Base):
    __tablename__ = 'product'

    # columns
    code = Column(String(Length.ID), primary_key=True, comment='종목코드')
    name = Column(String(Length.ID), comment='종목명')
    market_code = Column(String(Length.TYPE), comment='마켓코드')
    current = Column(Float, comment='현재가')
    minimum = Column(Float, comment='조회 기준일 최저가')
    maximum = Column(Float, comment='조회 기준일 최고가')
    opening = Column(Float, comment='조회 기준일 시가')
    base = Column(Float, comment='조회 기준일 전일종가')

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
    def list(cls, market: str = None, only_oversea: bool = False, session: Session = None):
        query = session.query(cls)

        if only_oversea:
            return query.filter(cls.market_code != MarketCode.KRX).all()

        if market is None:
            return query.all()

        else:
            return query.filter(cls.market_code == market).all()

    @classmethod
    @provide_session
    def truncate(cls, session: Session = None):
        session.query(cls).delete()

    @classmethod
    @provide_session
    def update(cls, data: List[Dict], session: Session = None):
        session.bulk_update_mappings(cls, data)

    @classmethod
    @provide_session
    def insert(cls, items: List[Dict], session: Session = None):
        session.bulk_save_objects([cls(**item) for item in items])

    @property
    def quote_unit(self) -> Union[int, float]:
        if self.market_code in MarketCode.us_list():
            return 0.01

        else:
            if self.current < 1000:
                return 1
            elif self.current < 5000:
                return 5
            elif self.current < 10000:
                return 10
            elif self.current < 50000:
                return 50
            elif self.current < 100000:
                return 100
            elif self.current < 500000:
                return 500
            else:
                return 1000


class ProductHistory(Base):
    __tablename__ = 'product_history'

    # columns
    # id = Column(Integer(), primary_key=True, autoincrement=True)
    product_name = Column(String(Length.ID), ForeignKey('product.name'), primary_key=True, comment='종목명')
    standard_date = Column(String(Length.DATE), primary_key=True, comment='영업일자')
    minimum = Column(Float, comment='최저가')
    maximum = Column(Float, comment='최고가')
    opening = Column(Float, comment='시가')
    closing = Column(Float, comment='종가')
    volume = Column(Integer, comment='거래량')

    # relation
    product = relationship('Product', uselist=False, backref='history')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Portfolio(product_name='{self.product_name}')>"

    @property
    def market_code(self):
        return self.product.market_code

    @property
    def product_code(self):
        return self.product.code

    @property
    def current(self):
        return self.product.current

    @classmethod
    @provide_session
    def truncate(cls, session: Session = None):
        session.query(cls).delete()

    @classmethod
    @provide_session
    def delete(cls, product_name: str = None, session: Session = None):
        if product_name:
            session.query(cls).filter(cls.product_name == product_name).delete()
        else:
            session.query(cls).delete()

    @classmethod
    @provide_session
    def insert(cls, items: List[Dict], session: Session = None):
        session.bulk_save_objects([cls(**item) for item in items])
