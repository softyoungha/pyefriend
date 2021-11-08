import logging
import sys
from typing import Union, Optional
from contextlib import contextmanager
from PyQt5.QtWidgets import QApplication

from .api import DomesticApi, OverSeasApi
from .log import logger


# 상수
from .const import Target

app: Optional[QApplication] = None


def run_app():
    global app

    if app is None:
        app = QApplication(sys.argv)
        logger.info('Start APP')

    return app


def load_api(target: str,
             account: str,
             password: str) -> Union[DomesticApi, OverSeasApi]:
    # run app
    run_app()

    if target == Target.DOMESTIC:
        return DomesticApi(target_account=account, password=password)

    elif target == Target.OVERSEAS:
        return OverSeasApi(target_account=account, password=password)


@contextmanager
def api_context(target: str, account: str, password: str):
    """
    session생성

    :param target: 'domestic' / 'overseas'
    :return: session
    """
    assert target in (Target.DOMESTIC, Target.OVERSEAS), ""

    # run app
    run_app()

    try:
        # api
        if target == Target.DOMESTIC:
            api = DomesticApi(target_account=account, password=password)

        elif target == Target.OVERSEAS:
            api = OverSeasApi(target_account=account, password=password)

        yield api

    except Exception as e:
        raise

    finally:
        logger.info('exit context')


def domestic_context(account: str, password: str) -> DomesticApi:
    return api_context(target=Target.DOMESTIC,
                       account=account,
                       password=password)


def overseas_context(account: str, password: str) -> OverSeasApi:
    return api_context(target=Target.OVERSEAS,
                       account=account,
                       password=password)


