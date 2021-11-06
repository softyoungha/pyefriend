from typing import List, Dict
from sqlalchemy import Column, Integer, Text, String, JSON, Float, Index, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref, Session

from pyefriend.utils.orm_helper import provide_session
from .base import Base, Length


class Portfolio(Base):
    __tablename__ = 'portfolio'

    # columns
    product_name = Column(String(Length.ID), ForeignKey('product.name'), primary_key=True, comment='종목명')
    weight = Column(Float, comment='가중치(평가액)')
    last_price = Column(Float, comment='마지막 조회시 종목 금액')
    use_yn = Column(Boolean, default=False, comment='포함 여부')

    # relation
    product = relationship('Product', backref='portfolio')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Portfolio(product_name='{self.product_name}', weight='{self.weight}')>"

    @property
    @provide_session
    def product_code(self, session=None):
        return self.product.code

    @property
    @provide_session
    def market_code(self, session=None):
        return self.product.market_code

    @classmethod
    @provide_session
    def update_price(cls, data: List[Dict], session: Session = None):
        session.bulk_update_mappings(cls, data)
