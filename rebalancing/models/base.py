from typing import Optional

from sqlalchemy import MetaData, Column, Integer, DateTime, func, text
from sqlalchemy.ext.declarative import declarative_base

from rebalancing.settings import engine

# create metadata
metadata: Optional[MetaData] = MetaData(bind=engine)

# create base
Base = declarative_base(metadata=metadata)


# init
class Length:
    ID = 100
    TYPE = 30
    DESC = 5000
    DATE = 8


class NamedColumns:
    CreatedTime = lambda: Column(DateTime(timezone=True),
                                 nullable=False,
                                 server_default=func.created_time())
    UpdatedTime = lambda: Column(DateTime(timezone=True),
                                 nullable=False,
                                 server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    ID = lambda: Column(Integer(), primary_key=True, autoincrement=True)
