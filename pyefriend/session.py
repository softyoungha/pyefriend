from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from utils.config import Database

engine: Optional[Engine] = None
Session: Optional[scoped_session] = None


def configure_sqlalchemy_session(echo: bool = True):
    global engine
    global Session

    # set engine
    engine = create_engine(Database.SQLALCHEMY_CONN_STR, echo=echo)

    # set Session
    Session = scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=engine,
        )
    )