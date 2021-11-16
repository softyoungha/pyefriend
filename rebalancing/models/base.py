from typing import Optional

from sqlalchemy import MetaData, Column, Integer, DateTime, func, text
from sqlalchemy.orm import declarative_base, DeclarativeMeta

from rebalancing.settings import engine

# create metadata
metadata: Optional[MetaData] = MetaData(bind=engine)

# create base
Base: Optional[DeclarativeMeta] = declarative_base(metadata=metadata)


# init
class Length:
    ID = 100
    TYPE = 30
    DESC = 5000
    DATE = 8


class NamedColumns:
    CreatedTime = lambda: Column(DateTime(timezone=True),
                                 nullable=False,
                                 server_default=func.now())
    UpdatedTime = lambda: Column(DateTime(timezone=True),
                                 nullable=False,
                                 onupdate=func.now())
    ID = lambda: Column(Integer(), primary_key=True, autoincrement=True)
