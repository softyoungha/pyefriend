import os

from sqlalchemy import Column, Integer, Text, String, JSON, Float, Index, ForeignKey
from sqlalchemy.orm import relationship, backref

from .base import Base, NamedColumns, Length


class ProductMaster(Base):
    __tablename__ = 'product_master'

    # columns
    code = Column(String(Length.ID), primary_key=True, comment='종목코드')
    name = Column(String(Length.ID), comment='종목명')

    __table_args__ = (
        Index('idx_product_name', name, unique=True),
        # {'schema': 'product'}
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Portfolio(Base):
    __tablename__ = 'portfolio'

    # columns
    product = Column(String(Length.ID), ForeignKey('product_master.name'), primary_key=True, comment='종목명')
    weight = Column(Float, comment='가중치(평가액)')
    last_price = Column(Integer, comment='마지막 조회시 종목 금액')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)