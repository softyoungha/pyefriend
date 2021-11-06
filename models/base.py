from typing import Optional

from sqlalchemy import MetaData, Column, Integer, DateTime, func, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta
from utils.config import Database

metadata: Optional[MetaData] = MetaData(schema=Database.SQLALCHEMY_CONN_STR)

Base: DeclarativeMeta = declarative_base(metadata=metadata)


# init
class Length:
    ID = 100
    DESC = 5000


class NamedColumns:
    CreatedTime = lambda: Column(DateTime(timezone=True),
                                 nullable=False,
                                 server_default=func.now())
    UpdatedTime = lambda: Column(DateTime(timezone=True),
                                 nullable=False,
                                 server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    ID = lambda: Column(Integer(), primary_key=True, autoincrement=True)
