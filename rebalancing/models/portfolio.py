import os
import pandas as pd
from typing import List, Dict
from sqlalchemy import Column, Integer, Text, String, JSON, Float, Index, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref, Session

from pyefriend.const import MarketCode
from rebalancing.utils.orm_helper import provide_session
from .base import Base, Length


class Portfolio(Base):
    __tablename__ = 'portfolio'

    # columns
    product_name = Column(String(Length.ID), ForeignKey('product.name'), primary_key=True, comment='종목명')
    weight = Column(Float, comment='가중치(평가액)')
    use_yn = Column(Boolean, default=False, comment='포함 여부')

    # relation
    product = relationship('Product', uselist=False, backref='portfolio')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Portfolio(product_name='{self.product_name}', weight='{self.weight}')>"

    @property
    def market_code(self):
        return self.product.market_code

    @property
    def product_code(self):
        return self.product.code

    @property
    def current(self):
        return self.product.current

    @property
    def quote_unit(self):
        return self.product.quote_unit

    @classmethod
    @provide_session
    def update(cls, data: List[Dict], session: Session = None):
        session.bulk_update_mappings(cls, data)

    @classmethod
    @provide_session
    def insert(cls, items: List[dict], session: Session = None):
        session.bulk_save_objects([cls(**item) for item in items])

    @classmethod
    @provide_session
    def list(cls, domestic: bool, only_y: bool = True, session: Session = None):
        from .product import Product

        query = session.query(cls).join(Product)

        if only_y:
            query = query.filter(cls.use_yn == True)

        if domestic:
            query = query.filter(Product.market_code == MarketCode.KRX)
        else:
            query = query.filter(Product.market_code != MarketCode.KRX)

        return [
            (item.product_code,
             item.product_name,
             item.current,
             item.weight,
             item.quote_unit)
            for item in query.all()
        ]

