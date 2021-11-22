import os
import pandas as pd
from typing import Dict, List

from pyefriend_api.settings import BASE_DIR, logger
from pyefriend_api.models.base import metadata
from pyefriend_api.models import Setting


def init_db():
    metadata.create_all()
    logger.info('create_all: Done')

    Setting.initialize(first=True)
    logger.info('create_all: Done')


def reset_db():
    # drop tables
    metadata.drop_all()
    logger.info('drop_all: Done')

    # create tables
    init_db()
