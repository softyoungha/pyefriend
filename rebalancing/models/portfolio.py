import os
import pandas as pd
from typing import List, Dict
from sqlalchemy import Column, Integer, Text, String, JSON, Float, Index, ForeignKey, Boolean
from sqlalchemy.orm import relationship, backref, Session

from rebalancing.utils.orm_helper import provide_session
from .base import Base, Length


class Portfolio(Base):
    __tablename__ = 'portfolio'

    # columns
    product_name = Column(String(Length.ID), ForeignKey('product.name'), primary_key=True, comment='종목명')
    weight = Column(Float, comment='가중치(평가액)')
    planning_price = Column(Float, comment='')
    use_yn = Column(Boolean, default=False, comment='포함 여부')

    # relation
    product = relationship('Product', backref='portfolio')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<Portfolio(product_name='{self.product_name}', weight='{self.weight}')>"

    @property
    @provide_session
    def product_code(self, session: Session = None):
        return self.product.code

    @property
    @provide_session
    def market_code(self, session: Session = None):
        return self.product.market_code

    @property
    @provide_session
    def current(self, session: Session = None):
        return self.product.current

    @classmethod
    @provide_session
    def update(cls, data: List[Dict], session: Session = None):
        session.bulk_update_mappings(cls, data)

    @classmethod
    @provide_session
    def insert(cls, items: List[dict], session: Session = None):
        session.bulk_save_objects([cls(**item) for item in items])
