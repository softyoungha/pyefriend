from typing import Optional

from sqlalchemy import MetaData, Column, Integer, DateTime, func, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

from rebalancing.settings import engine

# create metadata
metadata: Optional[MetaData] = MetaData(bind=engine)

# create base
Base: DeclarativeMeta = declarative_base(metadata=metadata)


# init
class Length:
    ID = 100
    TYPE = 30
    DESC = 5000


class NamedColumns:
    CreatedTime = lambda: Column(DateTime(timezone=True),
                                 nullable=False,
                                 server_default=func.now())
    UpdatedTime = lambda: Column(DateTime(timezone=True),
                                 nullable=False,
                                 server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    ID = lambda: Column(Integer(), primary_key=True, autoincrement=True)
