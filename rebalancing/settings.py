import os, sys
import logging

from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker

from rebalancing.config import Config, HOME_PATH
from rebalancing.utils.log import get_logger


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

engine: Optional[Engine] = None
Session: Optional[scoped_session] = None


logger = get_logger('re-balancing')


def prepare_syspath():
    if HOME_PATH not in sys.path:
        sys.path.append(HOME_PATH)


def configure_sqlalchemy_session(echo: bool = False):
    global engine
    global Session

    # set engine
    engine = create_engine(Config.get('database', 'SQLALCHEMY_CONN_STR'),
                           echo=echo)
    logger.info('create engine')

    # set Session
    Session = scoped_session(
        sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=engine,
        )
    )
    logger.info('create Session')


def initialize():
    prepare_syspath()
    configure_sqlalchemy_session()
