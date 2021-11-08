"""
# Helper

- QApplication 을 하나만 유지
- api를 with절로 활용하거나, 단일 api를 불러오는 데에 용이
"""

import sys
from typing import Union, Optional
from contextlib import contextmanager
from PyQt5.QtWidgets import QApplication

from .api import DomesticApi, OverSeasApi
from .log import logger
from .const import Target

# [Section] Variables

app: Optional[QApplication] = None


# [Section] Modules

def run_app():
    global app

    if app is None:
        app = QApplication(sys.argv)
        logger.info('Start APP')

    return app


def load_api(target: str, account: str, password: str, logger=None) -> Union[DomesticApi, OverSeasApi]:
    """
    api 로드
    :param target: 'domestic' / 'overseas'
    """
    assert target in (Target.DOMESTIC, Target.OVERSEAS), "target은 'domestic', 'overseas' 둘 중 하나만 입력 가능합니다."

    # run app
    run_app()

    if target == Target.DOMESTIC:
        return DomesticApi(target_account=account, password=password, logger=logger)

    elif target == Target.OVERSEAS:
        return OverSeasApi(target_account=account, password=password, logger=logger)


@contextmanager
def api_context(target: str, account: str, password: str, logger=logger) -> Union[DomesticApi, OverSeasApi]:
    """
    api 생성
    :param target: 'domestic' / 'overseas'
    """
    assert target in (Target.DOMESTIC, Target.OVERSEAS), "target은 'domestic', 'overseas' 둘 중 하나만 입력 가능합니다."

    # run app
    run_app()

    try:
        # api
        if target == Target.DOMESTIC:
            api = DomesticApi(target_account=account, password=password, logger=logger)

        elif target == Target.OVERSEAS:
            api = OverSeasApi(target_account=account, password=password, logger=logger)

        yield api

    except Exception as e:
        raise

    finally:
        logger.info('exit context')


def domestic_context(account: str, password: str, logger=None) -> DomesticApi:
    return api_context(target=Target.DOMESTIC,
                       account=account,
                       password=password,
                       logger=logger)


def overseas_context(account: str, password: str, logger=None) -> OverSeasApi:
    return api_context(target=Target.OVERSEAS,
                       account=account,
                       password=password,
                       logger=logger)
